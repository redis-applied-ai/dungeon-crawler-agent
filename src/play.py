import argparse
import datetime
import logging
import re
from typing import Any, Dict

import textworld.gym
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool

from redis import Redis


GAME = None


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


logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger(__name__)


redis_client = Redis(host="localhost", port=6379, db=0)
saver = RedisSaver(
    redis_client=redis_client,
)
saver.setup()


def get_score(text: str) -> int:
    """
    Get the score from the left hand status line.

    The left hand status line looks like this:
    [the player's surroundings] / [turn count] / [score]
    """
    score = re.findall(r" / (\d+) / (\d+)", text)
    if score:
        return int(score[0][1])
    else:
        return 0


scratchpad = {}


def get_scratchpad_key() -> str:
    """
    Get the key for the scratchpad for a specific game.
    """
    return f"scratchpad:{GAME}"


@tool
def read_scratchpad() -> dict[str, str]:
    """
    Read the contents of your scratchpad. These are notes you've taken to
    remember things about the game as you play it, including a map of the
    rooms you've visited.
    """
    logger.info("Reading scratchpad")
    key_ = get_scratchpad_key()
    return redis_client.json().get(key_) or {}  # type: ignore


@tool
def update_scratchpad(items: dict[str, Any]):
    """
    Update the items in your scratchpad. These are notes you're taking to
    remember things about the game as you play it. Updating your scratchpad
    replaces the previous contents of the scratchpad, so include all the items
    you want to remember.

    Use your scratchpad:
    1. To keep track of the rooms you've visited, including their exits, and
       any objects you've seen. A "map" key should be used to store this map
       of the rooms you've visited.
    2. Your reflections on the outcome of your last move and what it could
       mean for your strategy.

    For example:

    update_scratchpad(
        items={
            "map": {
                "Living Room": {
                    "description": "A cozy room with a fireplace",
                    "exits": {
                    "north": "Kitchen",
                    "east": "Hallway",
                    "down": "Basement"
                },
                "objects": ["sofa", "lamp"]
            },
            "Kitchen": {
                "description": "A small kitchen with granite countertops",
                "exits": {
                        "south": "Living Room",
                        "west": "Pantry",
                    },
                    "objects": ["knife", "apple"],
                },
            },
        },
        "reflections": [
            "The silver key did not open the door in the kitchen. I should try
            to find a different key to open the door in the kitchen.",
            "I should take the knife in case I can use it later.",
        ],
    )
    """
    key = get_scratchpad_key()
    # TODO: Partial updates
    logger.info("Updating scratchpad: %s", items)
    redis_client.json().set(key, "$", items)


TOOLS = {
    "read_scratchpad": read_scratchpad,
    "update_scratchpad": update_scratchpad,
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
    llm = state["llm"]
    response = llm.invoke(prompt)
    plan = response.text()
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
        
        Use your scratchpad tools to keep track of any information you need to
        remember. ALWAYS use the scratchpad tool to keep track of the rooms
        you've explored.
        
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
    obs, _, done, infos = env.step(command)
    text = env.render(mode="text")
    # Clean the render text using our helper
    print(text)
    # cleaned_text = clean_render(text)
    # print(cleaned_text)

    state["obs"] = obs
    state["score"] = get_score(text)
    state["done"] = done
    state["moves"] += 1
    state["history"].append(f"{command.strip('\n')}: {obs.strip('\n')}")

    # Reset the move count if the player has descended into the next level.
    for phrase in (
        "The metal groans under your weight!",
        "You descend into the workshop",
        "You carefully lower yourself through the hatch",
        "You carefully climb down the maintenance ladder",
    ):
        if phrase in text:
            state["moves"] = 0

    # The game doesn't always keep track of the turn number correctly.
    if state["moves"] >= 30:
        print("Game over! Too many moves.")
        state["game_outcome"] = "loss"
        state["done"] = True
    elif "Would you like to RESTART" in text:
        if "your ingenuity has won the day" in text:
            state["game_outcome"] = "win"
        else:
            state["game_outcome"] = "loss"
        state["done"] = True

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
    Evaluate your performance with extreme brevity. If your plan failed, try to
    evaluate why, and include enough detail that your feedback will make sense
    without access to the original plan. Focus on what you can do differently in
    the next attempt.

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
    feedback_entry = f"[{state['game_outcome']}] {new_feedback}"

    # If there are too many feedback items, summarize the oldest ones and add
    # the summary to the list.
    feedback_count = redis_client.llen(key)
    if feedback_count >= MAX_FEEDBACK_ITEMS:  # type: ignore
        feedback_items = redis_client.lrange(key, 0, -1)
        feedback_items = [item.decode() for item in feedback_items if item is not None]  # type: ignore
        old_feedback = "\n".join(feedback_items)

        prompt = f"""
        Summarize the following feedback about your performance in a game. This
        feedback was gathered from previous games you played. Use 100 words or
        less to capture only information useful for future games. Be sure to preserve
        information about which games were wins and which were losses.

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

    env_id = textworld.gym.register_game(args.game_path, max_episode_steps=50)
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
        ).bind_tools([read_scratchpad, update_scratchpad]),
        "turn": 0,
        "start": datetime.datetime.now(),
        "end_time": None,
        "level": 1,
    }

    GAME = args.game_path

    # Print the starting text.
    print(clean_render(text))

    conf = RunnableConfig(
        configurable={"thread_id": thread_id},
        recursion_limit=100,
    )
    compiled.invoke(initial_state, conf)
