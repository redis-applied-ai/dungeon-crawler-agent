import argparse
import datetime
import logging
import os
import re
from typing import Any, Dict

import textworld.gym
import dotenv
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool

from redis import Redis


dotenv.load_dotenv()


GAME = None
LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
MAX_STEPS = int(os.getenv("MAX_STEPS", "400"))


class State(MessagesState):
    obs: str
    score: int
    moves: int
    done: bool
    command: str
    starting_text: str
    history: list[str]
    past_feedback: str
    plan: str
    llm: ChatOpenAI
    game_outcome: str
    start: datetime.datetime
    end_time: datetime.datetime | None
    current_level: int


MAX_FEEDBACK_ITEMS = 20


logging.basicConfig(level=LOG_LEVEL)

# Suppress INFO logging from common libraries
logging.getLogger("httpx").setLevel(LOG_LEVEL)
logging.getLogger("langgraph").setLevel(LOG_LEVEL)
logging.getLogger("textworld").setLevel(LOG_LEVEL)
logging.getLogger("openai").setLevel(LOG_LEVEL)
logging.getLogger("redis").setLevel(LOG_LEVEL)
logging.getLogger("redisvl").setLevel(LOG_LEVEL)

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


redis_client = Redis(host="localhost", port=6379, db=0)
saver = RedisSaver(
    redis_client=redis_client,
)
saver.setup()


def get_score_change(text: str) -> int:
    """
    Get the score change from the game text.

    The game shows score changes like:
    [+2 points] or [-1 point]
    """
    # Look for [+N points] or [-N points] pattern
    score_change = re.findall(r"\[([+-]\d+) points?\]", text)
    if score_change:
        return int(score_change[0])

    return 0


THREAD_ID = None


def get_general_notes_key(thread_id: str) -> str:
    """Get the key for general game notes for a specific thread and game."""
    return f"notes:{thread_id}:{GAME}"


def get_room_memory_key(thread_id: str, room_name: str) -> str:
    """Get the key for room-specific memory for a specific thread, game, and room."""
    return f"room_memory:{thread_id}:{GAME}:{room_name}"


@tool
def read_general_notes() -> dict[str, Any]:
    """
    Read your general notes for this game session. These are notes about your
    overall strategy, goals, questions you're trying to answer, and high-level
    observations that apply across the entire game.

    Use this to store:
    - Your current goals and objectives
    - Questions you're trying to answer
    - Overall strategy and approach
    - Items you're carrying or looking for
    - General observations about the game mechanics
    """
    if THREAD_ID is None:
        raise ValueError("Thread ID not set")
    key = get_general_notes_key(THREAD_ID)
    return redis_client.json().get(key) or {}


@tool
def update_general_notes(contents: dict[str, Any]):
    """
    Update your general notes for this game session. These are notes about your
    overall strategy, goals, questions you're trying to answer, and high-level
    observations that apply across the entire game.

    Use this to store:
    - Your current goals and objectives
    - Questions you're trying to answer
    - Overall strategy and approach
    - Items you're carrying or looking for
    - General observations about the game mechanics

    Example:
    update_general_notes({
        "current_goals": [
            "Find the silver key to unlock the kitchen door",
            "Explore the basement for the treasure"
        ],
        "questions": [
            "What is the purpose of the strange device in the attic?",
            "How do I activate the magical portal?"
        ],
        "strategy": "Explore systematically, north to south, collecting all items",
        "inventory": ["rusty key", "wooden sword", "magic potion"],
        "observations": [
            "Doors require specific keys - keys are not universal",
            "Some NPCs give hints if you ask the right questions"
        ]
    })
    """
    if THREAD_ID is None:
        raise ValueError("Thread ID not set")
    key = get_general_notes_key(THREAD_ID)
    logger.info("Updating general notes: %s", contents)
    redis_client.json().set(key, "$", contents)


@tool
def get_room_memory(room_name: str) -> str:
    """
    Get your memory for a specific room. Call this when you enter a room to
    recall what you've learned about it in previous visits.

    The room memory is a natural language scratchpad containing:
    - Room description and layout
    - Exits and where they lead
    - Objects present in the room
    - NPCs in the room and their behavior
    - Actions you've tried and their results
    - Any puzzles or mechanisms in the room

    Args:
        room_name: The name of the room (e.g., "Kitchen", "Living Room")

    Returns:
        A string containing your notes about this room, or empty string if no memory exists
    """
    if THREAD_ID is None:
        raise ValueError("Thread ID not set")
    key = get_room_memory_key(THREAD_ID, room_name)
    memory = redis_client.get(key)
    return memory.decode() if memory else ""


@tool
def update_room_memory(room_name: str, memory: str):
    """
    Update your memory for a specific room. Call this after taking actions in
    a room to record what you've learned.

    Store information about:
    - Room description and layout
    - Exits and where they lead
    - Objects present in the room (and their states)
    - NPCs in the room and their behavior
    - Actions you've tried and their results
    - Any puzzles or mechanisms in the room
    - Changes that occur in the room over time

    Args:
        room_name: The name of the room (e.g., "Kitchen", "Living Room")
        memory: String containing your notes about this room

    Example:
    update_room_memory("Kitchen", '''
    KITCHEN
    Description: Small kitchen with granite countertops and a locked door
    Exits: south to Living Room, west to Pantry
    Objects:
    - knife: sharp kitchen knife (taken)
    - apple: red apple still on counter
    - locked door: needs silver key, rusty key did not work
    Actions tried:
    - use rusty key on door: failed
    - take knife: success
    - examine countertops: found nothing
    Puzzles: door requires silver key
    Last visited: turn 15
    ''')
    """
    if THREAD_ID is None:
        raise ValueError("Thread ID not set")
    key = get_room_memory_key(THREAD_ID, room_name)
    logger.info("Updating room memory for %s: %s", room_name, memory)
    redis_client.set(key, memory)


TOOLS = {
    "read_general_notes": read_general_notes,
    "update_general_notes": update_general_notes,
    "get_room_memory": get_room_memory,
    "update_room_memory": update_room_memory,
}


def game_feedback_key(thread_id: str) -> str:
    """A list containing the feedback from each game with the same thread ID."""
    return f"game_feedback:{thread_id}"


def plan_strategy(state: Dict, config: RunnableConfig) -> Dict:
    """
    Use the LLM to plan a strategy for the game.
    """
    prompt = f"""
    You are playing a text-based adventure game. Read the starting text of the
    game and create a plan to win the game. Make the plan a concise, bulleted
    list. Return only the plan, nothing else.

    <starting_text>
    The starting text of the game:
    {state["starting_text"]}
    </starting_text>
    
    <feedback_from_previous_games>
    {state["past_feedback"]}
    </feedback_from_previous_games>
    
    Your plan:
    """
    # Use LLM without tools for planning to avoid tool call conflicts
    planning_llm = ChatOpenAI(model=state["llm"].model_name)
    response = planning_llm.invoke(prompt)
    plan = response.content
    state["plan"] = plan
    print(f"<Thinking> My plan is: \n{plan}")
    return state


def generate_next_command(state: Dict, config: RunnableConfig) -> Dict:
    """
    Use the LLM to generate the next command.
    """
    past_feedback = (
        f"""
    <past_feedback>
        Feedback from past attempts to play this game:
        {state["past_feedback"]}
    </past_feedback>
    """
        if state["past_feedback"]
        else ""
    )

    prompt = f"""
        You are playing a text-based adventure game. Read the current
        observation and generate the next command. Return only the command,
        nothing else. Do not wrap the command in quotes.
        
        Use your memory tools to keep track of any information you need to
        remember:
        - Use get_room_memory() when you enter a room to recall what you know
        - Use update_room_memory() after actions to record new information
        - Use read_general_notes() and update_general_notes() for strategy and goals
        ALWAYS use these tools to maintain your understanding of the game.
        
        <starting_text>
        The starting text of the game:
        {state["starting_text"]}
        </starting_text>
        
        <plan>
        Your plan for winning the game:
        {state["plan"]}
        </plan>
        
        <history>
        Your moves so far:
        {state["history"]}
        </history>
        
        {past_feedback}
        
        The current observation is:
        {state["obs"]}

        Your next command:
        """
    llm = state["llm"]
    messages: list[BaseMessage] = [HumanMessage(prompt)]
    response = llm.invoke(messages)
    messages.append(response)

    # Handle tool calls in a loop
    while response.tool_calls:
        for call in response.tool_calls:
            name = call["name"]
            args = call["args"]

            tool = TOOLS.get(name)
            if tool is None:
                raise ValueError(f"Unknown tool: {name}")

            failed = False
            try:
                message = tool.invoke(args)
            except Exception as e:
                message = f"Error invoking tool {name}: {e}"
                logger.info(message)
                failed = True

            messages.append(
                ToolMessage(
                    tool_call_id=call["id"],
                    content=message,
                )
            )

            # Give the LLM a chance to fix its tool call and try again.
            if failed:
                response = llm.invoke(messages)

        # continue conversation
        response = llm.invoke(messages)
        messages.append(response)

    command = str(response.content).strip()
    state["command"] = command

    return state


def clean_render(text: str) -> str:
    """
    Clean up the rendered game text to align the status line with the rest of
    the text.
    """
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.startswith(">"):
            cleaned_lines.append(line.lstrip("> ").rstrip())
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def game_step(state: Dict) -> Dict:
    """
    Execute the generated command in the game environment.
    """
    command = state["command"]
    obs, reward, done, infos = env.step(command)
    logger.debug(
        f"env.step returned - Obs: {obs}, Reward: {reward}, Done: {done}, Infos: {infos}"
    )

    text = env.render(mode="text")
    if state["moves"] != 0:
        print(text)

    state["obs"] = obs
    score_change = get_score_change(text)
    state["score"] = state["score"] + score_change
    state["done"] = done
    state["moves"] += 1
    state["history"].append(f"{command.strip('\n')}: {obs.strip('\n')}")

    # The game doesn't always keep track of the turn number correctly.
    if state["moves"] >= MAX_STEPS:
        print("Game over! Too many moves.")
        state["game_outcome"] = "loss"
        state["done"] = True
    elif "Would you like to RESTART" in text:
        if "your ingenuity has won the day" in text:
            state["game_outcome"] = "win"
        else:
            state["game_outcome"] = "loss"
        state["done"] = True
    elif state["done"] and not state.get("game_outcome"):
        # TextWorld ended the game for some other reason
        print("Game ended unexpectedly by TextWorld environment.")
        state["game_outcome"] = "loss"

    return state.copy()


def game_over(state: State, config: RunnableConfig) -> State:
    """
    End the game by closing the environment and reporting the results.
    """
    state["end_time"] = datetime.datetime.now()
    time_taken = (state["end_time"] - state["start"]).total_seconds()
    thread_id = config.get("configurable", {}).get("thread_id", "demo-thread")
    key = game_feedback_key(thread_id)

    env.close()
    print(f"Game Over! Total moves: {state['moves']}; Score: {state['score']}")
    print(f"Game Outcome: {state['game_outcome']}")
    print(f"Time taken: {time_taken} seconds")

    prompt = f"""
    You are a language agent who has just played a text-based adventure game.
    Evaluate your performance. Evaluate which parts of your plan worked, and so
    are worth trying again on a subsequent play of the game, and which didn't,
    so shouldn't be tried again. Focus on what you can do differently in
    the next attempt. If you won, consider how you might win faster.
    
    <starting_text>
    The starting text of the game:
    {state["starting_text"]}
    </starting_text>
    
    <plan>
    Your plan for winning the game:
    {state["plan"]}
    </plan>

    <history>
    Your moves and the result of each move:
    {state["history"]}
    </history>

    <score>
    Your final score:
    {state["score"]}
    </score>

    <outcome>
    Game outcome:
    {state["game_outcome"]}
    </outcome>

    <time_taken>
    Time taken:
    {time_taken} seconds
    </time_taken>

    Your concise feedback:
    """

    llm = state["llm"]
    response = llm.invoke(prompt)
    new_feedback = str(response.content).strip()

    print("My feedback on the game: ", new_feedback)

    # Format the feedback entry with the outcome
    feedback_entry = f"""
    <game_date>
    {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </game_date>
    
    <game_plan>
    {state["plan"]}
    </game_plan>

    <game_outcome>
    {state["game_outcome"]}
    </game_outcome>

    <game_feedback>
    {new_feedback}
    </game_feedback>
    """

    # If there are too many feedback items, summarize the oldest ones and add
    # the summary to the list.
    feedback_count = redis_client.llen(key)
    if feedback_count >= MAX_FEEDBACK_ITEMS:  # type: ignore
        feedback_items = redis_client.lrange(key, 0, -1)
        feedback_items = [item.decode() for item in feedback_items if item is not None]  # type: ignore
        old_feedback = "\n".join(feedback_items)

        prompt = f"""
        Summarize the following feedback about your performance in a game. This
        feedback was gathered from previous games you played. Capture only
        information useful for future games. Be sure to preserve information
        about which actions led to wins and which led to losses.

        <feedback_to_summarize>
        Your previous feedback:
        {old_feedback}
        </feedback_to_summarize>

        Summary of feedback:
        """
        response = state["llm"].invoke(prompt)
        old_feedback_summary = str(response.content).strip()
        redis_client.delete(key)
        redis_client.rpush(key, old_feedback_summary)

    # Add the latest feedback to the list.
    redis_client.rpush(key, feedback_entry)

    return state


# Build the LangGraph state graph.
graph = StateGraph(State)
graph.add_node("plan_strategy", plan_strategy)
graph.add_node("generate_next_command", generate_next_command)
graph.add_node("game_step", game_step)
graph.add_node("game_over", game_over)

# Wire up the nodes.
graph.add_edge(START, "plan_strategy")
graph.add_edge("plan_strategy", "generate_next_command")
graph.add_edge("generate_next_command", "game_step")

# Conditional edge: after game_step, if done then exit, else loop back to
# generate_next_command.
graph.add_conditional_edges(
    "game_step", lambda state: "game_over" if state["done"] else "generate_next_command"
)
graph.add_edge("game_over", END)
compiled = graph.compile(checkpointer=saver)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the game")
    parser.add_argument(
        "--thread-id",
        type=str,
        default="demo-thread",
        help="The thread ID to use for the game",
    )
    parser.add_argument(
        "--game-path",
        type=str,
        default="tw_games/custom_game.z8",
        help="The path to the game file to play",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="o4-mini",
        help="The model to use for the game",
    )
    parser.add_argument(
        "--clear-memory",
        action="store_true",
        default=False,
        help="Clear the memory of past games",
    )

    args = parser.parse_args()
    thread_id = args.thread_id

    # Set the global THREAD_ID for the tools
    THREAD_ID = thread_id

    env_id = textworld.gym.register_game(
        args.game_path, max_episode_steps=MAX_STEPS
    )  # TextWorld's count is sometimes different than ours
    env = textworld.gym.make(env_id)
    obs, infos = env.reset()
    text = env.render(mode="text")

    if args.clear_memory:
        redis_client.delete(game_feedback_key(thread_id))
        print("Cleared memory of past games")
        past_feedback = ""
    else:
        past_feedback_items = (
            redis_client.lrange(game_feedback_key(thread_id), 0, -1) or []
        )
        formatted_items = []

        for i, item in enumerate(past_feedback_items):  # type: ignore
            if item is not None:
                feedback_text = item.decode()
                # Check if the feedback already has the WIN/LOSS prefix
                if feedback_text.startswith("[WIN]") or feedback_text.startswith(
                    "[LOSS]"
                ):
                    formatted_items.append(f"Game {i}: {feedback_text}\n---")
                else:
                    # Legacy feedback without WIN/LOSS prefix
                    formatted_items.append(f"Game {i}: \n{feedback_text}\n---")

        past_feedback = "\n".join(formatted_items)

    initial_state = {
        "obs": obs,
        "score": 0,
        "moves": 0,
        "done": False,
        "command": "",
        "history": [],
        "starting_text": text,
        "past_feedback": past_feedback,
        "plan": "",
        "llm": ChatOpenAI(
            model=args.model,
        ).bind_tools(
            [
                read_general_notes,
                update_general_notes,
                get_room_memory,
                update_room_memory,
            ]
        ),
        "turn": 0,
        "start": datetime.datetime.now(),
        "end_time": None,
        "level": 1,
        "game_outcome": "",
    }

    # Set the global GAME for the tools
    GAME = args.game_path

    conf = RunnableConfig(
        configurable={"thread_id": thread_id},
        recursion_limit=MAX_STEPS * 3,
    )

    print(text)

    compiled.invoke(initial_state, conf)
