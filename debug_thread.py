#!/usr/bin/env python3
"""
Comprehensive debug tool to inspect all memory and ASTM data for a specific thread.

Examples:
  python debug_thread.py --list-threads                 # List all available threads
  python debug_thread.py final-test                     # Full debug report for thread
  python debug_thread.py final-test --summary           # Just show data summary
  python debug_thread.py final-test --astm-only         # Only show ASTM model
  python debug_thread.py final-test --memory-only       # Only show memory data
  python debug_thread.py final-test --checkpoints       # Include checkpoint data
"""

import argparse
import json
import sys
from datetime import datetime
from redis import Redis
from typing import Dict, List, Any

def format_rule(rule_data):
    """Format a rule for readable display."""
    condition = rule_data.get('condition', {}).get('predicates', {})
    action = rule_data.get('action', {})
    outcome = rule_data.get('outcome', {})
    
    print(f"    Rule (confidence: {rule_data.get('confidence', 'N/A'):.2f}, observations: {rule_data.get('observations', 'N/A')}):")
    print(f"      IF: {json.dumps(condition, indent=8)[2:-2] if condition else 'No conditions'}")
    
    verb = action.get('verb', '')
    objects = ' '.join(action.get('objects', []))
    targets = ' '.join(action.get('targets', []))
    action_str = f"{verb} {objects} {targets}".strip()
    print(f"      ACTION: {action_str or 'No action'}")
    
    print(f"      THEN:")
    if outcome.get('additions'):
        print(f"        Add: {json.dumps(outcome['additions'], indent=2)}")
    if outcome.get('removals'):
        print(f"        Remove: {json.dumps(outcome['removals'], indent=2)}")
    if outcome.get('modifications'):
        print(f"        Modify: {json.dumps(outcome['modifications'], indent=2)}")
    if not any([outcome.get('additions'), outcome.get('removals'), outcome.get('modifications')]):
        print(f"        (No changes)")

def inspect_astm_model(redis_client, thread_id: str, game_path: str = None):
    """Inspect ASTM model for a thread."""
    # Find ASTM model key for this thread
    if game_path:
        model_key = f"astm_model:{thread_id}:{game_path}"
    else:
        # Search for any ASTM model with this thread
        pattern = f"astm_model:{thread_id}:*"
        keys = redis_client.keys(pattern)
        if not keys:
            print("❌ No ASTM model found for this thread")
            return
        model_key = keys[0].decode() if isinstance(keys[0], bytes) else keys[0]
    
    try:
        model_data = redis_client.json().get(model_key)
        if not model_data:
            print("❌ ASTM model exists but has no data")
            return
        
        print(f"🧠 ASTM Model: {model_key}")
        print(f"   Saved at: {model_data.get('saved_at', 'Unknown')}")
        print(f"   Current turn: {model_data.get('current_turn', 'Unknown')}")
        
        accuracy = model_data.get('prediction_accuracy', [])
        if accuracy:
            avg_acc = sum(accuracy) / len(accuracy)
            print(f"   Prediction accuracy: {avg_acc:.2%} (over {len(accuracy)} predictions)")
        else:
            print(f"   Prediction accuracy: No predictions yet")
        
        model = model_data.get('model', {})
        stats = model.get('statistics', {})
        
        print(f"   Statistics:")
        print(f"     Total rules: {stats.get('total_rules', 0)}")
        print(f"     Universal rules: {stats.get('universal_rules', 0)}")
        print(f"     Local rules: {stats.get('local_rules', 0)}")
        print(f"     Locations known: {stats.get('locations_known', 0)}")
        print(f"     Meta patterns: {stats.get('meta_patterns', 0)}")
        
        # Show rules summary
        universal_rules = model.get('universal_rules', [])
        local_rules = model.get('local_rules', {})
        
        if universal_rules:
            print(f"\n   Universal Rules ({len(universal_rules)}):")
            for i, rule in enumerate(universal_rules):
                print(f"   Rule {i+1}:")
                format_rule(rule)
                print()
        
        if local_rules:
            total_local = sum(len(rules) for rules in local_rules.values())
            print(f"   Local Rules ({total_local} total across {len(local_rules)} locations):")
            for location, rules in local_rules.items():
                print(f"     Location: {location} ({len(rules)} rules)")
                for i, rule in enumerate(rules):
                    print(f"     Rule {i+1}:")
                    format_rule(rule)
                    print()
        
        meta_patterns = model.get('meta_patterns', {})
        if meta_patterns:
            print(f"   Meta Patterns ({len(meta_patterns)}):")
            for pattern_name, pattern_data in meta_patterns.items():
                print(f"     {pattern_name}: {json.dumps(pattern_data, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error inspecting ASTM model: {e}")

def inspect_game_feedback(redis_client, thread_id: str):
    """Inspect game feedback history for a thread."""
    feedback_key = f"game_feedback:{thread_id}"
    
    try:
        feedback_list = redis_client.lrange(feedback_key, 0, -1)
        if not feedback_list:
            print("❌ No game feedback found for this thread")
            return
        
        print(f"🎮 Game Feedback History ({len(feedback_list)} entries):")
        
        for i, feedback_bytes in enumerate(feedback_list):
            feedback = feedback_bytes.decode()
            print(f"\n   Game {i+1}:")
            
            # Parse feedback sections
            lines = feedback.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('<game_'):
                    current_section = line[1:-1]  # Remove < >
                    continue
                elif line.startswith('<'):
                    continue  # End tag
                elif current_section:
                    print(f"     {current_section}: {line}")
                    current_section = None
                elif line:
                    print(f"     {line[:100]}{'...' if len(line) > 100 else ''}")
    
    except Exception as e:
        print(f"❌ Error inspecting game feedback: {e}")

def inspect_room_memories(redis_client, thread_id: str, game_path: str = None):
    """Inspect room memories for a thread."""
    if game_path:
        pattern = f"room_memory:{thread_id}:{game_path}:*"
    else:
        pattern = f"room_memory:{thread_id}:*"
    
    try:
        room_keys = redis_client.keys(pattern)
        if not room_keys:
            print("❌ No room memories found for this thread")
            return
        
        print(f"🏠 Room Memories ({len(room_keys)} rooms):")
        
        for key in sorted(room_keys):
            key_str = key.decode() if isinstance(key, bytes) else key
            room_name = key_str.split(':')[-1]  # Extract room name
            
            memory = redis_client.get(key_str)
            if memory:
                memory_text = memory.decode()
                print(f"\n   Room: {room_name}")
                print(f"   Memory ({len(memory_text)} chars):")
                # Show first few lines
                lines = memory_text.split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
                if len(memory_text.split('\n')) > 10:
                    print(f"     ... ({len(memory_text.split('\n')) - 10} more lines)")
            else:
                print(f"   Room: {room_name} (no data)")
    
    except Exception as e:
        print(f"❌ Error inspecting room memories: {e}")

def inspect_general_notes(redis_client, thread_id: str, game_path: str = None):
    """Inspect general notes for a thread."""
    if game_path:
        notes_key = f"notes:{thread_id}:{game_path}"
    else:
        # Search for any notes with this thread
        pattern = f"notes:{thread_id}:*"
        keys = redis_client.keys(pattern)
        if not keys:
            print("❌ No general notes found for this thread")
            return
        notes_key = keys[0].decode() if isinstance(keys[0], bytes) else keys[0]
    
    try:
        notes_data = redis_client.json().get(notes_key)
        if not notes_data:
            print("❌ No general notes found for this thread")
            return
        
        print(f"📝 General Notes: {notes_key}")
        
        for key, value in notes_data.items():
            print(f"   {key}:")
            if isinstance(value, list):
                for item in value:
                    print(f"     - {item}")
            elif isinstance(value, dict):
                print(f"     {json.dumps(value, indent=6)}")
            else:
                print(f"     {value}")
    
    except Exception as e:
        print(f"❌ Error inspecting general notes: {e}")

def inspect_thread_checkpoints(redis_client, thread_id: str, limit: int = 5):
    """Inspect recent LangGraph checkpoints for debugging."""
    pattern = f"checkpoint_*:{thread_id}:*"
    
    try:
        checkpoint_keys = redis_client.keys(pattern)
        if not checkpoint_keys:
            print("❌ No checkpoints found for this thread")
            return
        
        print(f"🔄 LangGraph Checkpoints ({len(checkpoint_keys)} total, showing latest {limit}):")
        
        # Group by type
        blob_keys = [k for k in checkpoint_keys if b'checkpoint_blob:' in k or 'checkpoint_blob:' in str(k)]
        write_keys = [k for k in checkpoint_keys if b'checkpoint_write:' in k or 'checkpoint_write:' in str(k)]
        
        print(f"   Blob checkpoints: {len(blob_keys)}")
        print(f"   Write checkpoints: {len(write_keys)}")
        
        # Show some recent blob data
        recent_blobs = sorted(blob_keys, reverse=True)[:limit]
        for key in recent_blobs:
            key_str = key.decode() if isinstance(key, bytes) else key
            try:
                # Extract field name from key
                parts = key_str.split(':')
                if len(parts) >= 4:
                    field_name = parts[3]
                    data = redis_client.get(key_str)
                    if data and len(data) < 200:  # Only show small data
                        print(f"   {field_name}: {data.decode()[:100]}...")
            except:
                continue
    
    except Exception as e:
        print(f"❌ Error inspecting checkpoints: {e}")

def get_thread_summary(redis_client, thread_id: str):
    """Get a summary of all data available for a thread."""
    # Search for all keys related to this thread
    patterns = [
        f"astm_model:{thread_id}:*",
        f"game_feedback:{thread_id}",
        f"room_memory:{thread_id}:*",
        f"notes:{thread_id}:*",
        f"checkpoint_*:{thread_id}:*"
    ]
    
    summary = {}
    total_keys = 0
    
    for pattern in patterns:
        keys = redis_client.keys(pattern)
        category = pattern.split(':')[0].replace('*', '').replace('checkpoint_', 'checkpoint')
        summary[category] = len(keys)
        total_keys += len(keys)
    
    return summary, total_keys

def main():
    parser = argparse.ArgumentParser(description="Debug all memory and ASTM data for a thread")
    parser.add_argument("thread_id", nargs='?', help="Thread ID to inspect")
    parser.add_argument("--game-path", type=str, help="Specific game path (optional)")
    parser.add_argument("--astm-only", action="store_true", help="Show only ASTM model")
    parser.add_argument("--memory-only", action="store_true", help="Show only memory data")
    parser.add_argument("--summary", action="store_true", help="Show only summary")
    parser.add_argument("--redis-port", type=int, default=6380, help="Redis port")
    parser.add_argument("--checkpoints", action="store_true", help="Include checkpoint inspection")
    parser.add_argument("--list-threads", action="store_true", help="List all available threads")
    
    args = parser.parse_args()
    
    redis_client = Redis(host='localhost', port=args.redis_port, db=0)
    
    try:
        redis_client.ping()
    except Exception as e:
        print(f"❌ Error connecting to Redis on port {args.redis_port}: {e}")
        sys.exit(1)
    
    if args.list_threads:
        # Find all unique thread IDs
        patterns = ["astm_model:*", "game_feedback:*", "room_memory:*", "notes:*"]
        thread_ids = set()
        
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            for key in keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                parts = key_str.split(':')
                if len(parts) >= 2:
                    thread_ids.add(parts[1])
        
        print(f"🧵 Available Threads ({len(thread_ids)}):")
        for thread_id in sorted(thread_ids):
            summary, total_keys = get_thread_summary(redis_client, thread_id)
            print(f"   {thread_id}: {total_keys} total keys")
            for category, count in summary.items():
                if count > 0:
                    print(f"     {category}: {count}")
        return
    
    if not args.thread_id:
        parser.print_help()
        print("\nError: thread_id is required unless using --list-threads")
        sys.exit(1)
    
    print(f"🔍 Thread Debug Report: {args.thread_id}")
    print("=" * 60)
    
    # Get summary first
    summary, total_keys = get_thread_summary(redis_client, args.thread_id)
    
    if args.summary:
        print(f"📊 Summary ({total_keys} total keys):")
        for category, count in summary.items():
            if count > 0:
                print(f"   {category}: {count} keys")
        return
    
    if total_keys == 0:
        print(f"❌ No data found for thread: {args.thread_id}")
        return
    
    print(f"📊 Data Summary: {total_keys} total keys")
    for category, count in summary.items():
        if count > 0:
            print(f"   {category}: {count}")
    print()
    
    # Show different sections based on flags
    if not args.memory_only:
        inspect_astm_model(redis_client, args.thread_id, args.game_path)
        print()
    
    if not args.astm_only:
        inspect_game_feedback(redis_client, args.thread_id)
        print()
        
        inspect_room_memories(redis_client, args.thread_id, args.game_path)
        print()
        
        inspect_general_notes(redis_client, args.thread_id, args.game_path)
        print()
    
    if args.checkpoints:
        inspect_thread_checkpoints(redis_client, args.thread_id)

if __name__ == "__main__":
    main()