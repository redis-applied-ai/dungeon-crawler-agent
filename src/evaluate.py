#!/usr/bin/env python3
"""
Evaluation framework for the dungeon crawler agent.

Tests agent performance with different configurations and memory strategies
to measure learning effectiveness and performance improvements.
"""

import argparse
import datetime
import json
import os
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import redis


@dataclass
class GameResult:
    """Results from a single game run."""
    run_id: int
    outcome: str  # 'win', 'loss', or 'timeout'
    score: int
    moves: int
    time_seconds: float
    memory_enabled: bool
    astm_enabled: bool
    model: str
    thread_id: str
    timestamp: str
    plan: str = ""
    feedback: str = ""
    memory_usage: Dict = None

    def to_dict(self) -> Dict:
        return {
            'run_id': self.run_id,
            'outcome': self.outcome,
            'score': self.score,
            'moves': self.moves,
            'time_seconds': self.time_seconds,
            'memory_enabled': self.memory_enabled,
            'astm_enabled': self.astm_enabled,
            'model': self.model,
            'thread_id': self.thread_id,
            'timestamp': self.timestamp,
            'plan': self.plan,
            'feedback': self.feedback,
            'memory_usage': self.memory_usage or {}
        }


@dataclass
class EvaluationConfig:
    """Configuration for an evaluation run."""
    name: str
    model: str
    max_steps: int
    num_runs: int
    game_path: str
    memory_enabled: bool
    astm_enabled: bool
    clear_memory_between_runs: bool
    base_thread_id: str

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'model': self.model,
            'max_steps': self.max_steps,
            'num_runs': self.num_runs,
            'game_path': self.game_path,
            'memory_enabled': self.memory_enabled,
            'astm_enabled': self.astm_enabled,
            'clear_memory_between_runs': self.clear_memory_between_runs,
            'base_thread_id': self.base_thread_id
        }


@dataclass
class EvaluationResults:
    """Aggregated results from an evaluation."""
    config: EvaluationConfig
    results: List[GameResult]
    win_rate: float
    avg_score: float
    avg_moves_to_win: float
    avg_time_seconds: float
    score_std: float
    moves_std: float
    timestamp: str

    def to_dict(self) -> Dict:
        return {
            'config': self.config.to_dict(),
            'results': [r.to_dict() for r in self.results],
            'summary': {
                'win_rate': self.win_rate,
                'avg_score': self.avg_score,
                'avg_moves_to_win': self.avg_moves_to_win,
                'avg_time_seconds': self.avg_time_seconds,
                'score_std': self.score_std,
                'moves_std': self.moves_std,
                'total_runs': len(self.results),
                'wins': len([r for r in self.results if r.outcome == 'win']),
                'losses': len([r for r in self.results if r.outcome == 'loss']),
                'timeouts': len([r for r in self.results if r.outcome == 'timeout'])
            },
            'timestamp': self.timestamp
        }


class GameRunner:
    """Runs individual games and captures results."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6380, db=0)
    
    def run_game(self, config: EvaluationConfig, run_id: int) -> GameResult:
        """Run a single game and return results."""
        thread_id = f"{config.base_thread_id}-run-{run_id:03d}"
        
        # Clear memory if requested
        if config.clear_memory_between_runs:
            self._clear_memory_for_thread(thread_id)
        
        # Prepare command - use uv run to ensure proper virtual environment
        cmd = [
            "uv", "run", "python", "src/play.py",
            "--thread-id", thread_id,
            "--game-path", config.game_path,
            "--model", config.model
        ]
        
        # Set environment variables
        env = os.environ.copy()
        env['MAX_STEPS'] = str(config.max_steps)
        env['ASTM_ENABLED'] = str(config.astm_enabled).lower()
        
        if not config.memory_enabled:
            # Disable memory by clearing relevant Redis keys before each run
            self._disable_memory_for_thread(thread_id)
        
        if not config.astm_enabled:
            # Disable ASTM by clearing ASTM models
            self._disable_astm_for_thread(thread_id)
        
        print(f"Run {run_id:2d}/{config.num_runs}: Starting game with {config.model} "
              f"(memory={'on' if config.memory_enabled else 'off'}, "
              f"astm={'on' if config.astm_enabled else 'off'})")
        
        # Run the game
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per game
            )
            end_time = time.time()
            
            # Debug: print subprocess errors if game fails immediately
            if result.returncode != 0:
                print(f"    ERROR: Game subprocess failed with return code {result.returncode}")
                if result.stderr:
                    print(f"    STDERR: {result.stderr[:200]}...")
                if result.stdout:
                    print(f"    STDOUT: {result.stdout[:200]}...")
            
            # Parse results from output
            outcome, score, moves = self._parse_game_output(result.stdout, result.stderr)
            
            # Collect memory usage stats if memory is enabled
            memory_usage = None
            if config.memory_enabled:
                memory_usage = self._get_memory_usage(thread_id)
            
            return GameResult(
                run_id=run_id,
                outcome=outcome,
                score=score,
                moves=moves,
                time_seconds=end_time - start_time,
                memory_enabled=config.memory_enabled,
                astm_enabled=config.astm_enabled,
                model=config.model,
                thread_id=thread_id,
                timestamp=datetime.datetime.now().isoformat(),
                memory_usage=memory_usage
            )
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            return GameResult(
                run_id=run_id,
                outcome='timeout',
                score=0,
                moves=config.max_steps,
                time_seconds=end_time - start_time,
                memory_enabled=config.memory_enabled,
                astm_enabled=config.astm_enabled,
                model=config.model,
                thread_id=thread_id,
                timestamp=datetime.datetime.now().isoformat()
            )
    
    def _clear_memory_for_thread(self, thread_id: str):
        """Clear all memory for a specific thread."""
        # Clear game feedback
        feedback_key = f"game_feedback:{thread_id}"
        self.redis_client.delete(feedback_key)
        
        # Clear general notes and room memories (pattern matching)
        pattern_keys = [
            f"notes:{thread_id}:*",
            f"room_memory:{thread_id}:*",
            f"astm_model:{thread_id}:*"  # Clear ASTM models
        ]
        for pattern in pattern_keys:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
    
    def _disable_memory_for_thread(self, thread_id: str):
        """Disable memory by preventing memory tools from working."""
        # For memory-disabled runs, we'll clear memory before each run
        # The tools will still be called but won't have any data
        self._clear_memory_for_thread(thread_id)
    
    def _disable_astm_for_thread(self, thread_id: str):
        """Disable ASTM by clearing ASTM models."""
        # Clear ASTM model data for this thread
        pattern = f"astm_model:{thread_id}:*"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def _parse_game_output(self, stdout: str, stderr: str) -> Tuple[str, int, int]:
        """Parse game output to extract outcome, score, and moves."""
        outcome = 'loss'  # Default
        score = 0
        moves = 0
        
        # Look for game over information
        for line in stdout.split('\n'):
            if "Game Over!" in line and "Total moves:" in line:
                # Extract moves and score from line like: "Game Over! Total moves: 25; Score: 12"
                parts = line.split(';')
                if len(parts) >= 2:
                    # Extract moves
                    moves_part = parts[0].split(':')[-1].strip()
                    try:
                        moves = int(moves_part)
                    except ValueError:
                        pass
                    
                    # Extract score
                    score_part = parts[1].split(':')[-1].strip()
                    try:
                        score = int(score_part)
                    except ValueError:
                        pass
            
            elif "Game Outcome:" in line:
                if "win" in line.lower():
                    outcome = 'win'
                elif "loss" in line.lower():
                    outcome = 'loss'
            
            elif "Game over! Too many moves." in line:
                outcome = 'timeout'
        
        return outcome, score, moves
    
    def _get_memory_usage(self, thread_id: str) -> Dict:
        """Get memory usage statistics for a thread."""
        stats = {
            'general_notes_size': 0,
            'room_memories_count': 0,
            'room_memories_total_size': 0,
            'feedback_entries': 0
        }
        
        # Count general notes
        notes_key = f"notes:{thread_id}:*"
        notes_keys = self.redis_client.keys(notes_key)
        for key in notes_keys:
            data = self.redis_client.json().get(key)
            if data:
                stats['general_notes_size'] += len(str(data))
        
        # Count room memories
        room_pattern = f"room_memory:{thread_id}:*"
        room_keys = self.redis_client.keys(room_pattern)
        stats['room_memories_count'] = len(room_keys)
        for key in room_keys:
            memory = self.redis_client.get(key)
            if memory:
                stats['room_memories_total_size'] += len(memory.decode())
        
        # Count feedback entries
        feedback_key = f"game_feedback:{thread_id}"
        stats['feedback_entries'] = self.redis_client.llen(feedback_key) or 0
        
        return stats


class Evaluator:
    """Main evaluation coordinator."""
    
    def __init__(self, output_dir: str = "evals"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.runner = GameRunner()
    
    def run_evaluation(self, config: EvaluationConfig) -> EvaluationResults:
        """Run a complete evaluation with the given configuration."""
        print(f"\n=== Starting Evaluation: {config.name} ===")
        print(f"Model: {config.model}")
        print(f"Max Steps: {config.max_steps}")
        print(f"Runs: {config.num_runs}")
        print(f"Memory: {'Enabled' if config.memory_enabled else 'Disabled'}")
        print(f"ASTM: {'Enabled' if config.astm_enabled else 'Disabled'}")
        print(f"Thread ID: {config.base_thread_id}")
        
        results = []
        for run_id in range(1, config.num_runs + 1):
            result = self.runner.run_game(config, run_id)
            results.append(result)
            
            # Print progress
            print(f"  → Run {run_id:2d}: {result.outcome.upper():<7} "
                  f"Score: {result.score:3d} Moves: {result.moves:3d} "
                  f"Time: {result.time_seconds:.1f}s")
        
        # Calculate summary statistics
        win_rate = len([r for r in results if r.outcome == 'win']) / len(results)
        scores = [r.score for r in results]
        avg_score = statistics.mean(scores)
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        
        wins = [r for r in results if r.outcome == 'win']
        avg_moves_to_win = statistics.mean([r.moves for r in wins]) if wins else 0
        moves_std = statistics.stdev([r.moves for r in results]) if len(results) > 1 else 0
        
        avg_time = statistics.mean([r.time_seconds for r in results])
        
        eval_results = EvaluationResults(
            config=config,
            results=results,
            win_rate=win_rate,
            avg_score=avg_score,
            avg_moves_to_win=avg_moves_to_win,
            avg_time_seconds=avg_time,
            score_std=score_std,
            moves_std=moves_std,
            timestamp=datetime.datetime.now().isoformat()
        )
        
        # Save results
        self._save_results(eval_results)
        
        # Print summary
        self._print_summary(eval_results)
        
        return eval_results
    
    def compare_evaluations(self, eval1: EvaluationResults, eval2: EvaluationResults):
        """Compare two evaluation results."""
        print(f"\n=== Comparison: {eval1.config.name} vs {eval2.config.name} ===")
        
        print(f"Win Rate:     {eval1.win_rate:.1%} → {eval2.win_rate:.1%} "
              f"({'+'if eval2.win_rate > eval1.win_rate else ''}{(eval2.win_rate - eval1.win_rate):.1%})")
        
        print(f"Avg Score:    {eval1.avg_score:.1f} → {eval2.avg_score:.1f} "
              f"({'+'if eval2.avg_score > eval1.avg_score else ''}{eval2.avg_score - eval1.avg_score:.1f})")
        
        if eval1.avg_moves_to_win > 0 and eval2.avg_moves_to_win > 0:
            print(f"Avg Moves (wins): {eval1.avg_moves_to_win:.1f} → {eval2.avg_moves_to_win:.1f} "
                  f"({'+'if eval2.avg_moves_to_win > eval1.avg_moves_to_win else ''}{eval2.avg_moves_to_win - eval1.avg_moves_to_win:.1f})")
        
        print(f"Avg Time:     {eval1.avg_time_seconds:.1f}s → {eval2.avg_time_seconds:.1f}s "
              f"({'+'if eval2.avg_time_seconds > eval1.avg_time_seconds else ''}{eval2.avg_time_seconds - eval1.avg_time_seconds:.1f}s)")
    
    def _save_results(self, results: EvaluationResults):
        """Save evaluation results to disk."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{results.config.name}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        
        print(f"\nResults saved to: {filepath}")
    
    def _print_summary(self, results: EvaluationResults):
        """Print evaluation summary."""
        wins = len([r for r in results.results if r.outcome == 'win'])
        losses = len([r for r in results.results if r.outcome == 'loss'])
        timeouts = len([r for r in results.results if r.outcome == 'timeout'])
        total_runs = len(results.results)
        
        print(f"\n=== Summary: {results.config.name} ===")
        print(f"Win Rate:        {results.win_rate:.1%} ({wins}/{total_runs})")
        print(f"Average Score:   {results.avg_score:.1f} ± {results.score_std:.1f}")
        
        if results.avg_moves_to_win > 0:
            print(f"Avg Moves (wins): {results.avg_moves_to_win:.1f}")
        
        print(f"Average Time:    {results.avg_time_seconds:.1f}s")
        print(f"Outcomes:        {wins} wins, {losses} losses, {timeouts} timeouts")


def create_preset_configs(model: str, game_path: str, base_thread_id: str) -> List[EvaluationConfig]:
    """Create preset evaluation configurations for memory comparison."""
    return [
        # Baseline: No memory, no ASTM
        EvaluationConfig(
            name=f"baseline_no_memory_{model}",
            model=model,
            max_steps=50,
            num_runs=20,
            game_path=game_path,
            memory_enabled=False,
            astm_enabled=False,
            clear_memory_between_runs=True,
            base_thread_id=f"{base_thread_id}_baseline"
        ),
        
        # Memory enabled, ASTM disabled, cleared between runs
        EvaluationConfig(
            name=f"memory_fresh_{model}",
            model=model,
            max_steps=50,
            num_runs=20,
            game_path=game_path,
            memory_enabled=True,
            astm_enabled=False,
            clear_memory_between_runs=True,
            base_thread_id=f"{base_thread_id}_fresh"
        ),
        
        # Memory enabled, ASTM disabled, persistent across runs (learning)
        EvaluationConfig(
            name=f"memory_learning_{model}",
            model=model,
            max_steps=50,
            num_runs=20,
            game_path=game_path,
            memory_enabled=True,
            astm_enabled=False,
            clear_memory_between_runs=False,
            base_thread_id=f"{base_thread_id}_learning"
        )
    ]


def create_astm_configs(model: str, game_path: str, base_thread_id: str) -> List[EvaluationConfig]:
    """Create ASTM-specific evaluation configurations."""
    return [
        # Baseline: No memory or ASTM
        EvaluationConfig(
            name=f"baseline_no_astm_{model}",
            model=model,
            max_steps=75,  # More steps to see learning effects
            num_runs=15,   # Fewer runs since ASTM takes more time
            game_path=game_path,
            memory_enabled=False,
            astm_enabled=False,
            clear_memory_between_runs=True,
            base_thread_id=f"{base_thread_id}_no_astm"
        ),
        
        # ASTM enabled, cleared between runs (fresh symbolic learning each time)
        EvaluationConfig(
            name=f"astm_fresh_{model}",
            model=model,
            max_steps=75,
            num_runs=15,
            game_path=game_path,
            memory_enabled=True,  # ASTM requires memory system
            astm_enabled=True,
            clear_memory_between_runs=True,
            base_thread_id=f"{base_thread_id}_astm_fresh"
        ),
        
        # ASTM enabled, persistent across runs (cumulative learning)
        EvaluationConfig(
            name=f"astm_learning_{model}",
            model=model,
            max_steps=75,
            num_runs=15,
            game_path=game_path,
            memory_enabled=True,
            astm_enabled=True,
            clear_memory_between_runs=False,
            base_thread_id=f"{base_thread_id}_astm_learning"
        )
    ]


def create_comprehensive_configs(model: str, game_path: str, base_thread_id: str) -> List[EvaluationConfig]:
    """Create comprehensive evaluation configurations testing meaningful combinations."""
    return [
        # Pure baseline: No memory, no ASTM
        EvaluationConfig(
            name=f"baseline_{model}",
            model=model,
            max_steps=50,
            num_runs=10,
            game_path=game_path,
            memory_enabled=False,
            astm_enabled=False,
            clear_memory_between_runs=True,
            base_thread_id=f"{base_thread_id}_baseline"
        ),
        
        # Memory without ASTM (traditional memory tools only)
        EvaluationConfig(
            name=f"memory_only_{model}",
            model=model,
            max_steps=50,
            num_runs=10,
            game_path=game_path,
            memory_enabled=True,
            astm_enabled=False,
            clear_memory_between_runs=False,
            base_thread_id=f"{base_thread_id}_memory_only"
        ),
        
        # ASTM with memory (symbolic learning + memory tools)
        EvaluationConfig(
            name=f"astm_with_memory_{model}",
            model=model,
            max_steps=50,
            num_runs=10,
            game_path=game_path,
            memory_enabled=True,
            astm_enabled=True,
            clear_memory_between_runs=False,
            base_thread_id=f"{base_thread_id}_astm"
        )
    ]


def main():
    parser = argparse.ArgumentParser(description="Evaluate dungeon crawler agent performance")
    parser.add_argument("--model", type=str, default="o3-mini", 
                       help="Model to use for evaluation")
    parser.add_argument("--game-path", type=str, default="games/dungeon.ulx",
                       help="Path to the game file")
    parser.add_argument("--max-steps", type=int, default=None,
                       help="Maximum steps per game")
    parser.add_argument("--num-runs", type=int, default=None,
                       help="Number of runs per evaluation")
    parser.add_argument("--thread-id", type=str, default="eval",
                       help="Base thread ID for evaluation")
    parser.add_argument("--preset", choices=["memory-comparison", "astm-evaluation", "comprehensive", "custom"], 
                       default="memory-comparison",
                       help="Use preset configurations or custom")
    parser.add_argument("--memory-enabled", action="store_true", default=True,
                       help="Enable memory tools (for custom mode)")
    parser.add_argument("--astm-enabled", action="store_true", default=False,
                       help="Enable ASTM system (for custom mode)")
    parser.add_argument("--name", type=str, default=None,
                       help="Custom evaluation name")
    
    args = parser.parse_args()
    
    # Validate preset vs custom parameter conflicts
    if args.preset in ["memory-comparison", "astm-evaluation", "comprehensive"]:
        conflicting_params = []
        preset_config = {
            "memory-comparison": {"max_steps": 50, "num_runs": 20},
            "astm-evaluation": {"max_steps": 75, "num_runs": 15},
            "comprehensive": {"max_steps": 50, "num_runs": 10}
        }
        config = preset_config[args.preset]
        
        # Check if user overrode any preset defaults
        if args.max_steps is not None and args.max_steps != config["max_steps"]:
            conflicting_params.append(f"--max-steps {args.max_steps} (preset uses {config['max_steps']})")
        if args.num_runs is not None and args.num_runs != config["num_runs"]:
            conflicting_params.append(f"--num-runs {args.num_runs} (preset uses {config['num_runs']})")
        if args.thread_id != "eval":
            conflicting_params.append(f"--thread-id {args.thread_id} (preset uses eval_*)")
        if not args.memory_enabled:
            conflicting_params.append("--memory-enabled False (preset uses multiple memory configs)")
        if args.astm_enabled:
            conflicting_params.append("--astm-enabled True (preset controls ASTM settings)")
        if args.name:
            conflicting_params.append(f"--name {args.name} (preset generates names automatically)")
        
        if conflicting_params:
            print(f"ERROR: Cannot use custom parameters with --preset {args.preset}")
            if args.preset == "memory-comparison":
                print("The memory-comparison preset runs 3 evaluations with fixed configurations:")
                print("  - 20 runs each, 50 steps max, automatic naming")
            elif args.preset == "astm-evaluation":
                print("The astm-evaluation preset runs 3 ASTM evaluations with fixed configurations:")
                print("  - 15 runs each, 75 steps max, automatic naming")
            else:  # comprehensive
                print("The comprehensive preset runs 3 meaningful evaluations:")
                print("  - 10 runs each, 50 steps max, automatic naming")
                print("  - Tests: baseline, memory-only, ASTM+memory")
            print("")
            print("Conflicting parameters detected:")
            for param in conflicting_params:
                print(f"  - {param}")
            print("")
            print("Solutions:")
            print("  1. Use --preset custom to respect your custom parameters:")
            print(f"     python src/evaluate.py --preset custom --model {args.model} --num-runs {args.num_runs or 20} --max-steps {args.max_steps or 50} --astm-enabled")
            print("  2. Remove conflicting parameters to use the preset as-is:")
            print(f"     python src/evaluate.py --preset {args.preset} --model {args.model}")
            print("")
            sys.exit(1)
    
    evaluator = Evaluator()
    
    if args.preset == "memory-comparison":
        # Run comprehensive memory comparison
        configs = create_preset_configs(args.model, args.game_path, args.thread_id)
        results = []
        
        for config in configs:
            result = evaluator.run_evaluation(config)
            results.append(result)
        
        # Compare results
        if len(results) >= 2:
            print(f"\n{'='*60}")
            evaluator.compare_evaluations(results[0], results[1])  # baseline vs fresh memory
            evaluator.compare_evaluations(results[1], results[2])  # fresh vs learning memory
            evaluator.compare_evaluations(results[0], results[2])  # baseline vs learning memory
    
    elif args.preset == "astm-evaluation":
        # Run ASTM-specific evaluation
        configs = create_astm_configs(args.model, args.game_path, args.thread_id)
        results = []
        
        for config in configs:
            result = evaluator.run_evaluation(config)
            results.append(result)
        
        # Compare results
        if len(results) >= 2:
            print(f"\n{'='*60}")
            print("=== ASTM SYSTEM EVALUATION RESULTS ===")
            evaluator.compare_evaluations(results[0], results[1])  # baseline vs ASTM fresh
            evaluator.compare_evaluations(results[1], results[2])  # ASTM fresh vs ASTM learning
            evaluator.compare_evaluations(results[0], results[2])  # baseline vs ASTM learning
    
    elif args.preset == "comprehensive":
        # Run comprehensive evaluation testing all combinations
        configs = create_comprehensive_configs(args.model, args.game_path, args.thread_id)
        results = []
        
        for config in configs:
            result = evaluator.run_evaluation(config)
            results.append(result)
        
        # Compare results
        if len(results) >= 3:
            print(f"\n{'='*60}")
            print("=== COMPREHENSIVE SYSTEM EVALUATION RESULTS ===")
            print("\nBaseline vs Memory-Only:")
            evaluator.compare_evaluations(results[0], results[1])  # baseline vs memory
            print("\nBaseline vs ASTM+Memory:")
            evaluator.compare_evaluations(results[0], results[2])  # baseline vs ASTM
            print("\nMemory-Only vs ASTM+Memory:")
            evaluator.compare_evaluations(results[1], results[2])  # memory vs ASTM
    
    else:
        # Custom evaluation - use sensible defaults if not specified
        config = EvaluationConfig(
            name=args.name or f"custom_{args.model}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            model=args.model,
            max_steps=args.max_steps or 50,
            num_runs=args.num_runs or 20,
            game_path=args.game_path,
            memory_enabled=args.memory_enabled,
            astm_enabled=args.astm_enabled,
            clear_memory_between_runs=False,
            base_thread_id=args.thread_id
        )
        
        evaluator.run_evaluation(config)


if __name__ == "__main__":
    main()