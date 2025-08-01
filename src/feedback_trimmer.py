#!/usr/bin/env python3
"""
Feedback trimming system to extract only the most actionable insights from game feedback.
"""

import json
import re
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI


def extract_actionable_feedback(feedback_text: str, outcome: str, llm: ChatOpenAI) -> Dict[str, any]:
    """
    Extract only the most actionable insights from verbose feedback.
    
    Args:
        feedback_text: Raw feedback text from the agent
        outcome: Game outcome (win/loss)  
        llm: LLM for processing
        
    Returns:
        Trimmed feedback with key insights
    """
    
    prompt = f"""
    Extract ONLY the most actionable insights from this game feedback. Focus on:
    1. Specific commands/verbs that work vs don't work
    2. Critical puzzle solutions or breakthroughs
    3. Fatal mistakes to avoid
    4. Winning strategies (if outcome was win)
    
    Game outcome: {outcome}
    
    Original feedback:
    {feedback_text}
    
    Return a JSON object with these keys:
    - "working_commands": ["command1", "command2"] - Commands that definitely work
    - "failed_commands": ["command1", "command2"] - Commands that definitely don't work  
    - "key_insights": ["insight1", "insight2"] - Maximum 3 most important discoveries
    - "fatal_mistakes": ["mistake1", "mistake2"] - Critical errors that led to failure
    - "next_priority": "single most important thing to try next"
    
    Keep each item under 50 characters. Be extremely concise and specific.
    """
    
    try:
        response = llm.invoke(prompt)
        # Try to parse as JSON
        trimmed = json.loads(response.content)
        return trimmed
    except:
        # Fallback to simple extraction if JSON parsing fails
        return extract_simple_insights(feedback_text, outcome)


def extract_simple_insights(feedback_text: str, outcome: str) -> Dict[str, any]:
    """Simple fallback extraction using regex patterns."""
    
    # Extract working commands (look for successful patterns)
    working_commands = []
    success_patterns = [
        r'"([^"]*)" (?:worked|succeeded|was effective)',
        r'(?:use|using|try) "([^"]*)" (?:worked|succeeded)',
        r'Successfully.*?(?:use|used|try|tried) "([^"]*)"'
    ]
    
    for pattern in success_patterns:
        matches = re.findall(pattern, feedback_text, re.IGNORECASE)
        working_commands.extend(matches[:3])  # Limit to 3
    
    # Extract failed commands
    failed_commands = []
    fail_patterns = [
        r'"([^"]*)" (?:failed|didn\'t work|was unsuccessful)',
        r'(?:failed to|couldn\'t) "([^"]*)"',
        r'"([^"]*)" (?:not recognized|unrecognized)'
    ]
    
    for pattern in fail_patterns:
        matches = re.findall(pattern, feedback_text, re.IGNORECASE)
        failed_commands.extend(matches[:3])  # Limit to 3
    
    # Extract key insights (look for important realizations)
    key_insights = []
    if "bronze lever" in feedback_text.lower():
        key_insights.append("bronze lever goes in control panel")
    if "wrench" in feedback_text.lower() and "cogsworth" in feedback_text.lower():
        key_insights.append("wrench repairs Cogsworth but parser finicky")
    if "elevator hatch" in feedback_text.lower():
        key_insights.append("control panel opens elevator hatch")
    
    # Extract fatal mistakes
    fatal_mistakes = []
    if "time" in feedback_text.lower() and ("alarm" in feedback_text.lower() or "moves" in feedback_text.lower()):
        fatal_mistakes.append("ran out of time/moves")
    if "stuck" in feedback_text.lower():
        fatal_mistakes.append("got stuck on puzzle")
    
    # Determine next priority based on outcome and content
    next_priority = "focus on main objective"
    if outcome == "loss":
        if "cogsworth" in feedback_text.lower():
            next_priority = "try different verbs for Cogsworth"
        elif "hatch" in feedback_text.lower():
            next_priority = "get through elevator hatch faster"
    
    return {
        "working_commands": working_commands[:3],
        "failed_commands": failed_commands[:3], 
        "key_insights": key_insights[:3],
        "fatal_mistakes": fatal_mistakes[:2],
        "next_priority": next_priority
    }


def consolidate_feedback_history(feedback_history: List[Dict], llm: ChatOpenAI, max_items: int = 5) -> List[Dict]:
    """
    Consolidate feedback history by merging similar insights and keeping only the most recent/relevant.
    
    Args:
        feedback_history: List of feedback dictionaries
        llm: LLM for processing
        max_items: Maximum number of items to keep
        
    Returns:
        Consolidated feedback list
    """
    
    if len(feedback_history) <= max_items:
        return feedback_history
    
    # Keep the most recent items
    recent_items = feedback_history[-max_items:]
    
    # Aggregate all working/failed commands to avoid repetition
    all_working = set()
    all_failed = set() 
    all_insights = set()
    all_mistakes = set()
    
    for item in feedback_history:
        all_working.update(item.get("working_commands", []))
        all_failed.update(item.get("failed_commands", []))
        all_insights.update(item.get("key_insights", []))
        all_mistakes.update(item.get("fatal_mistakes", []))
    
    # Create a consolidated summary item
    consolidated = {
        "game_date": "consolidated",
        "game_outcome": "summary",
        "working_commands": list(all_working)[:5],
        "failed_commands": list(all_failed)[:5],
        "key_insights": list(all_insights)[:5],
        "fatal_mistakes": list(all_mistakes)[:3],
        "next_priority": recent_items[-1].get("next_priority", "focus on winning")
    }
    
    # Return consolidated summary plus most recent individual items
    return [consolidated] + recent_items[-3:]


def format_trimmed_feedback(trimmed: Dict) -> str:
    """Format trimmed feedback for storage."""
    
    def format_list(items, prefix=""):
        if not items:
            return f"{prefix}None"
        return f"{prefix}" + ", ".join(items)
    
    return f"""TRIMMED FEEDBACK:
✅ Working: {format_list(trimmed.get('working_commands', []))}
❌ Failed: {format_list(trimmed.get('failed_commands', []))}
💡 Insights: {format_list(trimmed.get('key_insights', []))}
⚠️ Mistakes: {format_list(trimmed.get('fatal_mistakes', []))}
🎯 Next: {trimmed.get('next_priority', 'Focus on main objective')}"""


def process_feedback_for_storage(
    raw_feedback: str,
    plan: str, 
    outcome: str,
    llm: ChatOpenAI,
    existing_history: Optional[List[str]] = None
) -> str:
    """
    Process raw feedback into a trimmed, actionable format for storage.
    
    Args:
        raw_feedback: Original verbose feedback
        plan: Game plan
        outcome: win/loss
        llm: LLM for processing
        existing_history: Existing feedback history to consider
        
    Returns:
        Formatted feedback entry for storage
    """
    
    # Extract actionable insights
    trimmed = extract_actionable_feedback(raw_feedback, outcome, llm)
    
    # Format for storage
    formatted = f"""
<game_outcome>{outcome}</game_outcome>
<plan_summary>{plan[:200]}{'...' if len(plan) > 200 else ''}</plan_summary>
<actionable_feedback>
{format_trimmed_feedback(trimmed)}
</actionable_feedback>
"""
    
    return formatted.strip()


if __name__ == "__main__":
    # Test the trimming system
    import argparse
    
    parser = argparse.ArgumentParser(description="Test feedback trimming")
    parser.add_argument("--test-feedback", type=str, help="Test feedback text")
    parser.add_argument("--outcome", type=str, default="loss", help="Game outcome")
    
    args = parser.parse_args()
    
    if args.test_feedback:
        llm = ChatOpenAI(model="gpt-4")
        
        trimmed = extract_actionable_feedback(args.test_feedback, args.outcome, llm)
        print("Trimmed feedback:")
        print(json.dumps(trimmed, indent=2))
        
        print("\nFormatted for storage:")
        print(format_trimmed_feedback(trimmed))