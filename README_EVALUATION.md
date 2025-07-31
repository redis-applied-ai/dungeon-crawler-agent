# Agent Evaluation Framework

A comprehensive system for evaluating and analyzing the performance of the dungeon crawler agent with different memory configurations.

## Quick Start

### Run Complete Evaluation Suite
```bash
# Run with default settings (o3-mini model, 20 runs each condition)
./run_eval_suite.sh

# Run with specific model
./run_eval_suite.sh gpt-4 games/dungeon.ulx

# View results
cat evals/baseline_vs_fresh_*_report.txt
```

### Manual Evaluation
```bash
# Single evaluation (custom configuration)
python src/evaluate.py --model o3-mini --num-runs 10 --max-steps 50 --name "test_run"

# Memory comparison preset (baseline, fresh memory, learning memory)
python src/evaluate.py --preset memory-comparison --model o3-mini

# List evaluation results
python src/analyze_evals.py --list
```

## Evaluation Types

### 1. Memory Impact Comparison
Tests three conditions:
- **Baseline**: No memory tools enabled
- **Fresh Memory**: Memory enabled but cleared between runs
- **Learning Memory**: Memory persists across runs (cumulative learning)

### 2. Key Metrics Tracked
- **Win Rate**: Percentage of successful game completions
- **Score**: Average points earned per game
- **Moves to Win**: Steps required for successful runs
- **Memory Usage**: Tool usage patterns and storage efficiency
- **Statistical Significance**: T-tests and chi-square tests for improvements

### 3. Analysis Features
- Progressive learning curves
- Memory usage statistics
- Statistical significance testing
- Visualization plots and reports

## Files and Structure

```
src/
├── evaluate.py          # Main evaluation runner
├── analyze_evals.py     # Statistical analysis and reporting
└── play.py             # Original game player (unchanged)

evals/                  # Results directory
├── *.json             # Raw evaluation data
├── *_report.txt       # Analysis reports  
└── *_analysis.png     # Visualization plots

run_eval_suite.sh      # Complete evaluation pipeline
requirements-eval.txt  # Additional dependencies for analysis
```

## Configuration Options

### Evaluation Parameters
```python
python src/evaluate.py \
    --model "o3-mini" \              # LLM model to use
    --game-path "games/dungeon.ulx" \ # Game file path
    --max-steps 50 \                 # Steps per game
    --num-runs 20 \                  # Runs per condition
    --thread-id "my_eval" \          # Base thread identifier
    --preset "memory-comparison"     # Use preset configs
```

### Analysis Options
```python
python src/analyze_evals.py \
    --baseline "baseline_file.json" \
    --memory "memory_file.json" \
    --output "comparison_name"
```

## Interpretation Guide

### Statistical Significance
- **p < 0.05**: Improvement is statistically significant
- **p ≥ 0.05**: Improvement may be due to random chance
- **Effect Size**: Relative improvement percentage shows practical significance

### Learning Indicators
- **Positive correlation** between run number and score indicates learning
- **Early vs Late** comparison shows adaptation over time
- **Moving averages** reveal performance trends

### Memory Effectiveness
- Compare baseline vs fresh memory for immediate tool benefit
- Compare fresh vs learning memory for cumulative learning benefit
- Memory usage statistics show tool adoption patterns

## Example Results Interpretation

```
Memory improves win rate by: +15.0%
Memory improves score by: +8.2
✓ Score improvement is statistically significant
✓ Win rate improvement is statistically significant

Score-vs-run correlation: r = 0.423, p = 0.0156
Learning trend: significant
```

This indicates:
1. Memory provides substantial performance benefits
2. Improvements are statistically reliable
3. Agent learns progressively over multiple runs
4. Both immediate memory access and cumulative learning contribute

## Troubleshooting

### Common Issues
- **Redis not running**: Start with `redis-server`
- **Game not found**: Build game with `make build`
- **Missing dependencies**: Install with `pip install -r requirements-eval.txt`
- **Permission errors**: Make script executable with `chmod +x run_eval_suite.sh`

### Performance Considerations
- Each evaluation run takes 5-15 minutes depending on model and game complexity
- Memory-learning evaluations may take longer as agent develops strategies
- Increase `--num-runs` for more statistical power (20+ recommended)
- Adjust `--max-steps` based on game complexity (50-100 typical range)

## Advanced Usage

### Custom Memory Strategies
Modify the memory tools in `play.py` and compare:
1. Run baseline evaluation
2. Implement memory changes
3. Run new evaluation
4. Compare results with analysis tools

### Multi-Model Comparison
```bash
for model in o3-mini gpt-4 claude-3-sonnet; do
    ./run_eval_suite.sh $model
done
```

### Long-term Learning Studies
Use persistent thread IDs across multiple evaluation sessions to study very long-term learning patterns.

## Research Applications

This framework enables systematic study of:
- **Memory Architecture**: Different memory organization strategies
- **Learning Algorithms**: How agents accumulate and apply knowledge
- **Model Comparisons**: Performance differences across LLMs
- **Game Difficulty**: Impact of puzzle complexity on learning
- **Transfer Learning**: Knowledge application across similar games

The evaluation system provides the quantitative foundation for improving agent performance and understanding AI learning in interactive environments.