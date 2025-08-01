# Dungeon Crawler Agent

An AI agent that plays interactive fiction games built with Inform 7, specifically designed to test and improve text-based game interactions using TextWorld.

IMPORTANT: ALWAYS USE THE VIRTUALENV AT .venv WHEN RUNNING COMMANDS

## Project Overview

This project combines:
- **Inform 7** - Interactive fiction development system for creating text games
- **TextWorld** - Microsoft Research's toolkit for generating and playing text-based games
- **uv** - Python dependency management and virtual environment tool
- **AI Agent** - LLM-powered player that learns to navigate and solve text adventures

## Quick Start

### Prerequisites
- Python 3.8+
- uv (Python package manager)
- Inform 7 (for game compilation)

### Setup
```bash
# Install dependencies
uv sync

# Compile the game
make build

# Test the agent
MAX_STEPS=50 python src/play.py --game-path games/dungeon.ulx --model o3-mini --thread new-game-2
```

## Game Development

The main game is located in `src/dungeon/Clockwork.inform/Source/story.ni` and features a steampunk clockwork tower escape scenario.

### Building the Game

The project uses a Makefile to handle Inform 7 compilation:

```bash
# Build the game (creates games/dungeon.ulx)
make build

# Clean build artifacts
make clean

# Build with different output format
OUTPUT_FORMAT=z8 make build  # Creates games/dungeon.z8
```

### Game Structure

- **Aerial Platform** - Starting location with NPCs and puzzles
- **Workshop** - Multi-room mechanical area with steam pipe repair puzzle
- **Control Room** - Elevator access with keypad puzzle
- **Storage Area** - Contains tools and helpful NPC (Marigold)
- **Machine Bay** - Alternative exit route

## Testing the Agent

### Basic Testing Commands

```bash
# Standard test run with 50 steps
MAX_STEPS=50 python src/play.py --game-path games/dungeon.ulx --model o3-mini --thread new-game-2

# Extended testing with more steps
MAX_STEPS=100 python src/play.py --game-path games/dungeon.ulx --model gpt-4 --thread extended-test

# Quick debugging run
MAX_STEPS=20 python src/play.py --game-path games/dungeon.ulx --model o3-mini --thread debug
```

### Key Parameters

- `MAX_STEPS` - Maximum number of game turns before timeout
- `--game-path` - Path to the compiled game file (.ulx or .z8)
- `--model` - LLM model to use (o3-mini, gpt-4, etc.)
- `--thread` - Thread identifier for logging/tracking

### Game Files

- `games/dungeon.ulx` - Main compiled game (Glulx format)
- `games/dungeon.z8` - Alternative Z-machine format
- Use `.ulx` for modern features, `.z8` for compatibility

## Development Workflow

1. **Edit Game**: Modify `src/dungeon/Clockwork.inform/Source/story.ni`
2. **Compile**: Run `make build` 
3. **Test Agent**: Use the test commands above
4. **Iterate**: Adjust game logic based on agent performance

## Key Features

### NPCs and Puzzles
- **Cogsworth** - Broken automaton who provides elevator codes when repaired
- **Marigold** - Chief Engineer affected by steam leak, rewards helpful actions
- **Steam Pipe Repair** - Multi-solution puzzle with extensive command recognition
- **Keypad Access** - Code-based progression system

### Agent Challenges
- Natural language understanding of game descriptions
- Tool usage and inventory management  
- NPC interaction and help-seeking behavior
- Alternative solution discovery
- Puzzle sequence reasoning

## Architecture

```
src/
├── play.py              # Main agent runner
├── dungeon/
│   └── Clockwork.inform/
│       └── Source/
│           └── story.ni # Inform 7 source code
games/
├── dungeon.ulx          # Compiled game
└── dungeon.z8           # Alternative format
```

## Memory System

The project uses the standard Claude Code memory protocol:
- `.ai/TASK_MEMORY.md` - Cross-session learning about game mechanics
- `.ai/agent-*.md` - Specialized agent memories
- Automatic memory updates after significant discoveries

## Troubleshooting

### Compilation Issues
- Ensure Inform 7 is installed in `/Applications/Inform.app`
- Check syntax in the .ni source file
- Use `make clean && make build` for clean rebuild

### Agent Performance
- Increase MAX_STEPS for complex puzzle sequences
- Try different models for varied problem-solving approaches
- Check game logs for common failure patterns

### Game Testing
- Use TextWorld's gym interface for automated testing
- Monitor agent decision-making patterns
- Adjust game hints based on common sticking points
