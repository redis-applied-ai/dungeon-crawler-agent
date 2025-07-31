#!/bin/bash
# Comprehensive evaluation suite for the dungeon crawler agent

set -e

# Configuration
MODEL=${1:-"o3-mini"}
GAME_PATH=${2:-"games/dungeon.ulx"}
THREAD_ID="eval_$(date +%Y%m%d_%H%M%S)"

echo "Starting evaluation suite for model: $MODEL"
echo "Game path: $GAME_PATH"
echo "Base thread ID: $THREAD_ID"
echo "================================"

# Install evaluation dependencies
echo "Installing evaluation dependencies..."
pip install -r requirements-eval.txt

# Check if game exists
if [ ! -f "$GAME_PATH" ]; then
    echo "Error: Game file $GAME_PATH not found!"
    echo "Please build the game first with: make build"
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Error: Redis server is not running!"
    echo "Please start Redis with: redis-server"
    exit 1
fi

# Run memory comparison evaluation
echo "Running comprehensive memory comparison evaluation..."
python src/evaluate.py \
    --model "$MODEL" \
    --game-path "$GAME_PATH" \
    --thread-id "$THREAD_ID" \
    --preset memory-comparison

# Wait a bit to ensure all files are written
sleep 2

# Find the most recent evaluation files
EVAL_DIR="evals"
BASELINE_FILE=$(ls -t "$EVAL_DIR"/baseline_no_memory_*.json 2>/dev/null | head -n1)
MEMORY_FRESH_FILE=$(ls -t "$EVAL_DIR"/memory_fresh_*.json 2>/dev/null | head -n1)
MEMORY_LEARNING_FILE=$(ls -t "$EVAL_DIR"/memory_learning_*.json 2>/dev/null | head -n1)

if [ -z "$BASELINE_FILE" ] || [ -z "$MEMORY_FRESH_FILE" ] || [ -z "$MEMORY_LEARNING_FILE" ]; then
    echo "Error: Could not find all evaluation result files"
    echo "Baseline: $BASELINE_FILE"
    echo "Memory Fresh: $MEMORY_FRESH_FILE" 
    echo "Memory Learning: $MEMORY_LEARNING_FILE"
    exit 1
fi

echo "Found evaluation files:"
echo "  Baseline: $(basename "$BASELINE_FILE")"
echo "  Memory Fresh: $(basename "$MEMORY_FRESH_FILE")"
echo "  Memory Learning: $(basename "$MEMORY_LEARNING_FILE")"

# Generate analysis reports
echo ""
echo "Generating analysis reports..."

# Compare baseline vs memory (fresh)
echo "Analyzing baseline vs fresh memory impact..."
python src/analyze_evals.py \
    --baseline "$(basename "$BASELINE_FILE")" \
    --memory "$(basename "$MEMORY_FRESH_FILE")" \
    --output "baseline_vs_fresh_${MODEL}"

# Compare fresh vs learning memory
echo "Analyzing fresh vs learning memory impact..."
python src/analyze_evals.py \
    --baseline "$(basename "$MEMORY_FRESH_FILE")" \
    --memory "$(basename "$MEMORY_LEARNING_FILE")" \
    --output "fresh_vs_learning_${MODEL}"

# Analyze learning progression
echo "Analyzing learning progression..."
python src/analyze_evals.py \
    --learning "$(basename "$MEMORY_LEARNING_FILE")" \
    --output "learning_progression_${MODEL}"

echo ""
echo "================================"
echo "Evaluation suite completed!"
echo ""
echo "Results summary:"
echo "  Evaluation files: $EVAL_DIR/"
echo "  Analysis reports: $EVAL_DIR/*_report.txt"
echo "  Visualization plots: $EVAL_DIR/*_analysis.png"
echo ""
echo "To view results:"
echo "  cat $EVAL_DIR/baseline_vs_fresh_${MODEL}_report.txt"
echo "  cat $EVAL_DIR/learning_progression_${MODEL}_report.txt"
echo "  open $EVAL_DIR/baseline_vs_fresh_${MODEL}_analysis.png"