#!/usr/bin/env python3
"""
Analysis tools for evaluation results.

Provides statistical analysis, visualization, and reporting for agent performance evaluations.
"""

import argparse
import json
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


class EvalAnalyzer:
    """Analyzes evaluation results and generates reports."""
    
    def __init__(self, evals_dir: str = "evals"):
        self.evals_dir = Path(evals_dir)
        if not self.evals_dir.exists():
            self.evals_dir.mkdir(exist_ok=True)
    
    def load_evaluation(self, filename: str) -> Dict:
        """Load a single evaluation result file."""
        filepath = self.evals_dir / filename
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def list_evaluations(self) -> List[str]:
        """List all available evaluation files."""
        return [f.name for f in self.evals_dir.glob("*.json")]
    
    def compare_memory_impact(self, baseline_file: str, memory_file: str) -> Dict:
        """Compare baseline vs memory-enabled performance."""
        baseline = self.load_evaluation(baseline_file)
        memory = self.load_evaluation(memory_file)
        
        baseline_results = [r for r in baseline['results']]
        memory_results = [r for r in memory['results']]
        
        # Statistical tests
        baseline_scores = [r['score'] for r in baseline_results]
        memory_scores = [r['score'] for r in memory_results]
        
        baseline_wins = [r['outcome'] == 'win' for r in baseline_results]
        memory_wins = [r['outcome'] == 'win' for r in memory_results]
        
        # T-test for scores
        score_ttest = stats.ttest_ind(baseline_scores, memory_scores)
        
        # Chi-square test for win rates
        contingency = [
            [sum(baseline_wins), len(baseline_wins) - sum(baseline_wins)],
            [sum(memory_wins), len(memory_wins) - sum(memory_wins)]
        ]
        chi2_test = stats.chi2_contingency(contingency)
        
        analysis = {
            'baseline': {
                'name': baseline['config']['name'],
                'win_rate': baseline['summary']['win_rate'],
                'avg_score': baseline['summary']['avg_score'],
                'score_std': baseline['summary']['score_std'],
                'total_runs': baseline['summary']['total_runs']
            },
            'memory': {
                'name': memory['config']['name'],
                'win_rate': memory['summary']['win_rate'],
                'avg_score': memory['summary']['avg_score'],
                'score_std': memory['summary']['score_std'],
                'total_runs': memory['summary']['total_runs']
            },
            'statistical_tests': {
                'score_ttest': {
                    'statistic': score_ttest.statistic,
                    'pvalue': score_ttest.pvalue,
                    'significant': score_ttest.pvalue < 0.05
                },
                'winrate_chi2': {
                    'statistic': chi2_test.statistic,
                    'pvalue': chi2_test.pvalue,
                    'significant': chi2_test.pvalue < 0.05
                }
            },
            'improvements': {
                'win_rate_improvement': memory['summary']['win_rate'] - baseline['summary']['win_rate'],
                'score_improvement': memory['summary']['avg_score'] - baseline['summary']['avg_score'],
                'relative_win_improvement': (memory['summary']['win_rate'] - baseline['summary']['win_rate']) / baseline['summary']['win_rate'] if baseline['summary']['win_rate'] > 0 else 0,
                'relative_score_improvement': (memory['summary']['avg_score'] - baseline['summary']['avg_score']) / baseline['summary']['avg_score'] if baseline['summary']['avg_score'] > 0 else 0
            }
        }
        
        return analysis
    
    def analyze_learning_progression(self, learning_file: str) -> Dict:
        """Analyze learning progression over sequential runs."""
        data = self.load_evaluation(learning_file)
        results = data['results']
        
        # Group into early vs late runs
        mid_point = len(results) // 2
        early_runs = results[:mid_point]
        late_runs = results[mid_point:]
        
        early_scores = [r['score'] for r in early_runs]
        late_scores = [r['score'] for r in late_runs]
        
        early_wins = [r['outcome'] == 'win' for r in early_runs]
        late_wins = [r['outcome'] == 'win' for r in late_runs]
        
        # Calculate moving averages
        window_size = min(5, len(results) // 4)
        if window_size > 0:
            moving_avg_scores = []
            moving_avg_winrates = []
            for i in range(window_size - 1, len(results)):
                window = results[i - window_size + 1:i + 1]
                avg_score = statistics.mean([r['score'] for r in window])
                win_rate = sum([r['outcome'] == 'win' for r in window]) / len(window)
                moving_avg_scores.append(avg_score)
                moving_avg_winrates.append(win_rate)
        else:
            moving_avg_scores = []
            moving_avg_winrates = []
        
        # Test for improvement over time
        run_numbers = list(range(1, len(results) + 1))
        scores = [r['score'] for r in results]
        
        # Correlation between run number and score
        score_correlation = stats.pearsonr(run_numbers, scores)
        
        analysis = {
            'config': data['config'],
            'total_runs': len(results),
            'early_vs_late': {
                'early_avg_score': statistics.mean(early_scores),
                'late_avg_score': statistics.mean(late_scores),
                'early_win_rate': sum(early_wins) / len(early_wins),
                'late_win_rate': sum(late_wins) / len(late_wins),
                'score_improvement': statistics.mean(late_scores) - statistics.mean(early_scores),
                'win_rate_improvement': sum(late_wins) / len(late_wins) - sum(early_wins) / len(early_wins)
            },
            'progression': {
                'moving_avg_scores': moving_avg_scores,
                'moving_avg_winrates': moving_avg_winrates,
                'window_size': window_size
            },
            'correlation': {
                'score_vs_run': {
                    'correlation': score_correlation.correlation,
                    'pvalue': score_correlation.pvalue,
                    'significant': score_correlation.pvalue < 0.05
                }
            },
            'all_results': results
        }
        
        return analysis
    
    def generate_plots(self, analysis_data: Dict, output_prefix: str):
        """Generate visualization plots for the analysis."""
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Agent Performance Analysis: {output_prefix}', fontsize=16)
        
        # Plot 1: Score distribution comparison (if comparing two conditions)
        if 'baseline' in analysis_data and 'memory' in analysis_data:
            ax1 = axes[0, 0]
            baseline_file = None
            memory_file = None
            
            # We need the original data for plotting - this is a limitation of the current design
            # For now, create a simple bar chart
            conditions = ['Baseline', 'Memory']
            win_rates = [analysis_data['baseline']['win_rate'], analysis_data['memory']['win_rate']]
            scores = [analysis_data['baseline']['avg_score'], analysis_data['memory']['avg_score']]
            
            x = np.arange(len(conditions))
            width = 0.35
            
            ax1.bar(x - width/2, win_rates, width, label='Win Rate', alpha=0.8)
            ax1_twin = ax1.twinx()
            ax1_twin.bar(x + width/2, scores, width, label='Avg Score', alpha=0.8, color='orange')
            
            ax1.set_xlabel('Condition')
            ax1.set_ylabel('Win Rate', color='blue')
            ax1_twin.set_ylabel('Average Score', color='orange')
            ax1.set_title('Performance Comparison')
            ax1.set_xticks(x)
            ax1.set_xticklabels(conditions)
            ax1.legend(loc='upper left')
            ax1_twin.legend(loc='upper right')
        
        # Plot 2: Learning progression (if we have progression data)
        if 'progression' in analysis_data:
            ax2 = axes[0, 1]
            if analysis_data['progression']['moving_avg_scores']:
                x = range(analysis_data['progression']['window_size'], len(analysis_data['all_results']) + 1)
                ax2.plot(x, analysis_data['progression']['moving_avg_scores'], 'b-', label='Score', marker='o')
                ax2_twin = ax2.twinx()
                ax2_twin.plot(x, analysis_data['progression']['moving_avg_winrates'], 'r-', label='Win Rate', marker='s')
                
                ax2.set_xlabel('Run Number')
                ax2.set_ylabel('Moving Average Score', color='blue')
                ax2_twin.set_ylabel('Moving Average Win Rate', color='red')
                ax2.set_title('Learning Progression')
                ax2.legend(loc='upper left')
                ax2_twin.legend(loc='upper right')
            else:
                ax2.text(0.5, 0.5, 'Not enough data\nfor progression analysis', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Learning Progression')
        
        # Plot 3: Run-by-run results
        ax3 = axes[1, 0]
        if 'all_results' in analysis_data:
            results = analysis_data['all_results']
            runs = [r['run_id'] for r in results]
            scores = [r['score'] for r in results]
            colors = ['green' if r['outcome'] == 'win' else 'red' if r['outcome'] == 'loss' else 'orange' 
                     for r in results]
            
            ax3.scatter(runs, scores, c=colors, alpha=0.7)
            ax3.set_xlabel('Run Number')
            ax3.set_ylabel('Score')
            ax3.set_title('Individual Run Results')
            
            # Add legend
            import matplotlib.patches as mpatches
            win_patch = mpatches.Patch(color='green', label='Win')
            loss_patch = mpatches.Patch(color='red', label='Loss') 
            timeout_patch = mpatches.Patch(color='orange', label='Timeout')
            ax3.legend(handles=[win_patch, loss_patch, timeout_patch])
        
        # Plot 4: Summary statistics
        ax4 = axes[1, 1]
        if 'improvements' in analysis_data:
            improvements = analysis_data['improvements']
            metrics = ['Win Rate\nImprovement', 'Score\nImprovement', 'Relative Win\nImprovement (%)', 'Relative Score\nImprovement (%)']
            values = [
                improvements['win_rate_improvement'] * 100,
                improvements['score_improvement'],
                improvements['relative_win_improvement'] * 100,
                improvements['relative_score_improvement'] * 100
            ]
            
            bars = ax4.bar(metrics, values, color=['green' if v > 0 else 'red' for v in values], alpha=0.7)
            ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
            ax4.set_ylabel('Improvement')
            ax4.set_title('Memory Impact Summary')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height > 0 else -0.5),
                        f'{value:.1f}', ha='center', va='bottom' if height > 0 else 'top')
        
        plt.tight_layout()
        plt.savefig(self.evals_dir / f'{output_prefix}_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"Plot saved as: {self.evals_dir / f'{output_prefix}_analysis.png'}")
    
    def generate_report(self, analysis_data: Dict, output_name: str):
        """Generate a comprehensive text report."""
        report_path = self.evals_dir / f'{output_name}_report.txt'
        
        with open(report_path, 'w') as f:
            f.write(f"Agent Performance Analysis Report\n")
            f.write(f"Generated: {pd.Timestamp.now()}\n")
            f.write("=" * 50 + "\n\n")
            
            if 'baseline' in analysis_data and 'memory' in analysis_data:
                f.write("MEMORY IMPACT ANALYSIS\n")
                f.write("-" * 20 + "\n")
                
                baseline = analysis_data['baseline']
                memory = analysis_data['memory']
                improvements = analysis_data['improvements']
                
                f.write(f"Baseline ({baseline['name']}):\n")
                f.write(f"  Win Rate: {baseline['win_rate']:.1%}\n")
                f.write(f"  Avg Score: {baseline['avg_score']:.1f} ± {baseline['score_std']:.1f}\n")
                f.write(f"  Total Runs: {baseline['total_runs']}\n\n")
                
                f.write(f"Memory Enabled ({memory['name']}):\n")
                f.write(f"  Win Rate: {memory['win_rate']:.1%}\n")
                f.write(f"  Avg Score: {memory['avg_score']:.1f} ± {memory['score_std']:.1f}\n")
                f.write(f"  Total Runs: {memory['total_runs']}\n\n")
                
                f.write("IMPROVEMENTS:\n")
                f.write(f"  Win Rate: {improvements['win_rate_improvement']:+.1%} (relative: {improvements['relative_win_improvement']:+.1%})\n")
                f.write(f"  Score: {improvements['score_improvement']:+.1f} (relative: {improvements['relative_score_improvement']:+.1%})\n\n")
                
                # Statistical significance
                f.write("STATISTICAL SIGNIFICANCE:\n")
                stats_data = analysis_data['statistical_tests']
                f.write(f"  Score T-test: p = {stats_data['score_ttest']['pvalue']:.4f} ({'significant' if stats_data['score_ttest']['significant'] else 'not significant'})\n")
                f.write(f"  Win Rate χ² test: p = {stats_data['winrate_chi2']['pvalue']:.4f} ({'significant' if stats_data['winrate_chi2']['significant'] else 'not significant'})\n\n")
            
            if 'early_vs_late' in analysis_data:
                f.write("LEARNING PROGRESSION ANALYSIS\n")
                f.write("-" * 28 + "\n")
                
                early_late = analysis_data['early_vs_late']
                f.write(f"Early runs avg score: {early_late['early_avg_score']:.1f}\n")
                f.write(f"Late runs avg score: {early_late['late_avg_score']:.1f}\n")
                f.write(f"Score improvement: {early_late['score_improvement']:+.1f}\n\n")
                
                f.write(f"Early runs win rate: {early_late['early_win_rate']:.1%}\n")
                f.write(f"Late runs win rate: {early_late['late_win_rate']:.1%}\n")
                f.write(f"Win rate improvement: {early_late['win_rate_improvement']:+.1%}\n\n")
                
                if 'correlation' in analysis_data:
                    corr = analysis_data['correlation']['score_vs_run']
                    f.write(f"Score-vs-run correlation: r = {corr['correlation']:.3f}, p = {corr['pvalue']:.4f}\n")
                    f.write(f"Learning trend: {'significant' if corr['significant'] else 'not significant'}\n\n")
        
        print(f"Report saved as: {report_path}")
        
        # Also print summary to console
        print("\n" + "="*50)
        print("ANALYSIS SUMMARY")
        print("="*50)
        
        if 'improvements' in analysis_data:
            improvements = analysis_data['improvements']
            print(f"Memory improves win rate by: {improvements['win_rate_improvement']:+.1%}")
            print(f"Memory improves score by: {improvements['score_improvement']:+.1f}")
            
            if analysis_data['statistical_tests']['score_ttest']['significant']:
                print("✓ Score improvement is statistically significant")
            else:
                print("✗ Score improvement is not statistically significant")
            
            if analysis_data['statistical_tests']['winrate_chi2']['significant']:
                print("✓ Win rate improvement is statistically significant")
            else:
                print("✗ Win rate improvement is not statistically significant")


def main():
    parser = argparse.ArgumentParser(description="Analyze evaluation results")
    parser.add_argument("--baseline", type=str, help="Baseline evaluation file")
    parser.add_argument("--memory", type=str, help="Memory-enabled evaluation file")
    parser.add_argument("--learning", type=str, help="Learning progression evaluation file")
    parser.add_argument("--list", action="store_true", help="List available evaluation files")
    parser.add_argument("--output", type=str, default="analysis", help="Output prefix for generated files")
    
    args = parser.parse_args()
    
    analyzer = EvalAnalyzer()
    
    if args.list:
        print("Available evaluation files:")
        for filename in analyzer.list_evaluations():
            print(f"  {filename}")
        return
    
    if args.baseline and args.memory:
        # Memory impact analysis
        analysis = analyzer.compare_memory_impact(args.baseline, args.memory)
        analyzer.generate_report(analysis, f"{args.output}_memory_impact")
        analyzer.generate_plots(analysis, f"{args.output}_memory_impact")
    
    elif args.learning:
        # Learning progression analysis
        analysis = analyzer.analyze_learning_progression(args.learning)
        analyzer.generate_report(analysis, f"{args.output}_learning")
        analyzer.generate_plots(analysis, f"{args.output}_learning")
    
    else:
        print("Please specify either --baseline and --memory for comparison, or --learning for progression analysis")
        print("Use --list to see available evaluation files")


if __name__ == "__main__":
    main()