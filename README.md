# Dungeon Crawler Agent

This repository contains an AI agent that plays Inform7 text adventure games, specifically designed for "Clockwork Descent". The agent uses LangGraph and LangChain with language models to navigate and solve the game autonomously.

## Features

- Language model-driven game agent that plans strategy and generates commands
- Memory system that learns from past attempts
- Spatial mapping through a scratchpad tool
- Checkpoint saving with Redis

## Requirements

- Python 3.12+
- Redis server running locally
- TextWorld library
- LangChain and LangGraph
- OpenAI API key (for Claude or OpenAI models)

## Setting Up Redis

Choose from multiple Redis deployment options:


1. [Redis Cloud](https://redis.io/try-free): Managed cloud database (free tier available)
2. [Redis Stack](https://redis.io/docs/getting-started/install-stack/docker/): Docker image for development
    ```bash
    docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
    ```
3. [Redis Enterprise](https://redis.io/enterprise/): Commercial, self-hosted database
4. [Azure Managed Redis](https://azure.microsoft.com/en-us/products/managed-redis): Fully managed Redis Enterprise on Azure

> Enhance your experience and observability with the free [Redis Insight GUI](https://redis.io/insight/).


## Installation

```bash
git clone https://github.com/yourusername/dungeon-crawler-agent.git
cd dungeon-crawler-agent
pip install .  # or uv pip install .
```

## Running the Agent
Run the `src/play.py` file to watch the agent play. Specify
the model with `--model` (only OpenAI models at the moment).

```bash
python src/play.py --game-path games/dungeon.ulx --model o4-mini
```

PS: The agent can play any Glulx or Z8 (Z-code, version 8) game you can find on
the internet. Just change `--game-path` to point to the game you want to play!

### Command Line Options

- `--game-path`: Path to a Glulx Z8 game file
- `--model`: Language model to use (default: o4-mini)
- `--thread-id`: ID for tracking memory between runs (helpful you want to try different tools, prompts, etc. while preserving the state of memory for another agent experiment)
- `--clear-memory`: Clear memory of past games

## Building the Game (Optional)

If you want to build the Z8 file from source:

1. Install Inform7
2. Run `make`

NOTE: This is optional - you can play with the provided game file directly.

## Modifying the Agent

The agent in `src/play.py` has lots of room for experimentation:

- Enhance the planning strategy by modifying the `plan_strategy` function
- Improve command generation in `generate_next_command`
- Experiment with memory management approaches
- Use different mapping structures (or track additional data) in the scratchpad
- Create better heuristics for game completion

## How It Works

The agent follows a state machine process:
1. Plans overall strategy based on game introduction
2. Generates commands using the language model
3. Executes commands in the game environment
4. Records results and builds a map in its scratchpad
5. Learns from wins and losses for future attempts
