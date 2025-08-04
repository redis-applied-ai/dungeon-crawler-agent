"""
Time profiling utilities for tracking performance of different operations.
"""

import time
import json
from contextlib import contextmanager
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class ProfileEntry:
    """Single timing measurement entry."""
    operation: str
    duration: float
    category: str
    details: Dict[str, Any]
    timestamp: float


class GameProfiler:
    """Profiles timing for different categories of operations in the game."""
    
    def __init__(self):
        self.entries: List[ProfileEntry] = []
        self.category_totals: Dict[str, float] = defaultdict(float)
        self.category_counts: Dict[str, int] = defaultdict(int)
        
    @contextmanager
    def profile(self, operation: str, category: str, **details):
        """Context manager to profile an operation."""
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            entry = ProfileEntry(
                operation=operation,
                duration=duration,
                category=category,
                details=details,
                timestamp=start_time
            )
            
            self.entries.append(entry)
            self.category_totals[category] += duration
            self.category_counts[category] += 1
            
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics by category."""
        summary = {}
        for category in self.category_totals:
            total_time = self.category_totals[category]
            count = self.category_counts[category]
            avg_time = total_time / count if count > 0 else 0
            
            summary[category] = {
                "total_time": round(total_time, 3),
                "count": count,
                "avg_time": round(avg_time, 3),
                "percentage": 0  # Will be calculated below
            }
        
        # Calculate percentages
        total_game_time = sum(self.category_totals.values())
        if total_game_time > 0:
            for category in summary:
                summary[category]["percentage"] = round(
                    (summary[category]["total_time"] / total_game_time) * 100, 1
                )
        
        return summary
    
    def get_detailed_entries(self, category: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Get detailed entries, optionally filtered by category."""
        entries = self.entries
        if category:
            entries = [e for e in entries if e.category == category]
        
        if limit:
            entries = entries[-limit:]  # Get most recent entries
            
        return [asdict(entry) for entry in entries]
    
    def print_report(self):
        """Print a formatted timing report."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("GAME PERFORMANCE PROFILING REPORT")
        print("="*60)
        
        # Sort by total time descending
        sorted_categories = sorted(summary.items(), key=lambda x: x[1]["total_time"], reverse=True)
        
        print(f"{'Category':<20} {'Total(s)':<10} {'Count':<8} {'Avg(s)':<10} {'%':<6}")
        print("-" * 60)
        
        for category, stats in sorted_categories:
            print(f"{category:<20} {stats['total_time']:<10} {stats['count']:<8} {stats['avg_time']:<10} {stats['percentage']:<6}")
        
        total_time = sum(s["total_time"] for s in summary.values())
        print("-" * 60)
        print(f"{'TOTAL':<20} {round(total_time, 3):<10}")
        
        # Show slowest individual operations
        print("\nSLOWEST INDIVIDUAL OPERATIONS:")
        print("-" * 40)
        slowest = sorted(self.entries, key=lambda x: x.duration, reverse=True)[:10]
        for entry in slowest:
            print(f"{entry.operation:<25} {round(entry.duration, 3)}s ({entry.category})")
    
    def save_to_file(self, filepath: str):
        """Save profiling data to JSON file."""
        data = {
            "summary": self.get_summary(),
            "entries": self.get_detailed_entries()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Global profiler instance
profiler = GameProfiler()