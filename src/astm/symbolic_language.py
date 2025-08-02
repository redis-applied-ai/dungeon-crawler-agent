"""
Symbolic Language: Environmental Transition Expressions (ETEs)

Core symbolic representation system for state transitions and rules.
"""

import re
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime


@dataclass
class StatePattern:
    """Represents a pattern that matches game states using predicate logic."""
    predicates: Dict[str, Any]  # e.g., {"in": "kitchen", "has": "key", "npc_state": {"cogsworth": "broken"}}
    
    def matches(self, other: 'StatePattern') -> bool:
        """Check if this pattern matches another state pattern."""
        for key, value in self.predicates.items():
            if key not in other.predicates:
                return False
            if isinstance(value, dict) and isinstance(other.predicates[key], dict):
                if not all(other.predicates[key].get(k) == v for k, v in value.items()):
                    return False
            elif other.predicates[key] != value:
                return False
        return True
    
    def similarity(self, other: 'StatePattern') -> float:
        """Calculate semantic similarity between state patterns."""
        all_keys = set(self.predicates.keys()) | set(other.predicates.keys())
        if not all_keys:
            return 1.0
        
        matching_keys = 0
        for key in all_keys:
            if key in self.predicates and key in other.predicates:
                if self.predicates[key] == other.predicates[key]:
                    matching_keys += 1
                elif isinstance(self.predicates[key], dict) and isinstance(other.predicates[key], dict):
                    # Partial match for nested dicts
                    common_subkeys = set(self.predicates[key].keys()) & set(other.predicates[key].keys())
                    if common_subkeys:
                        matching_subkeys = sum(1 for k in common_subkeys 
                                             if self.predicates[key][k] == other.predicates[key][k])
                        matching_keys += matching_subkeys / len(common_subkeys) * 0.5
        
        return matching_keys / len(all_keys)


@dataclass
class ActionPattern:
    """Represents an action taken by the agent."""
    verb: str
    objects: List[str]  
    targets: List[str] = None
    
    def __post_init__(self):
        if self.targets is None:
            self.targets = []
    
    def matches(self, other: 'ActionPattern') -> bool:
        """Check if this action pattern matches another."""
        return (self.verb == other.verb and 
                set(self.objects) == set(other.objects) and 
                set(self.targets) == set(other.targets))
    
    def similarity(self, other: 'ActionPattern') -> float:
        """Calculate similarity between action patterns."""
        verb_match = 1.0 if self.verb == other.verb else 0.0
        
        obj_overlap = len(set(self.objects) & set(other.objects))
        obj_total = len(set(self.objects) | set(other.objects))
        obj_sim = obj_overlap / obj_total if obj_total > 0 else 1.0
        
        tgt_overlap = len(set(self.targets) & set(other.targets))  
        tgt_total = len(set(self.targets) | set(other.targets))
        tgt_sim = tgt_overlap / tgt_total if tgt_total > 0 else 1.0
        
        return (verb_match + obj_sim + tgt_sim) / 3.0


@dataclass
class StateChange:
    """Represents changes to the game state."""
    additions: Dict[str, Any]    # New state elements
    removals: Dict[str, Any]     # Removed state elements  
    modifications: Dict[str, Any]  # Changed state elements
    
    def apply_to(self, state_pattern: StatePattern) -> StatePattern:
        """Apply this state change to a state pattern."""
        new_predicates = state_pattern.predicates.copy()
        
        # Apply removals
        for key, value in self.removals.items():
            if key in new_predicates:
                if isinstance(new_predicates[key], list) and value in new_predicates[key]:
                    new_predicates[key] = [v for v in new_predicates[key] if v != value]
                elif new_predicates[key] == value:
                    del new_predicates[key]
        
        # Apply modifications and additions
        new_predicates.update(self.modifications)
        new_predicates.update(self.additions)
        
        return StatePattern(new_predicates)


@dataclass  
class TransitionRule:
    """A symbolic rule representing a state transition."""
    condition: StatePattern
    action: ActionPattern
    outcome: StateChange
    confidence: float = 1.0
    observations: int = 1
    created_at: datetime = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def update_confidence(self, success: bool, decay_factor: float = 0.95):
        """Update rule confidence based on observation."""
        if success:
            self.confidence = min(1.0, self.confidence + (1.0 - self.confidence) * 0.1)
        else:
            self.confidence *= decay_factor
        self.observations += 1
        self.last_updated = datetime.now()
    
    def merge_with(self, other: 'TransitionRule') -> 'TransitionRule':
        """Merge this rule with another compatible rule."""
        if not (self.condition.similarity(other.condition) > 0.8 and 
                self.action.similarity(other.action) > 0.8):
            raise ValueError("Rules are not compatible for merging")
        
        # Weighted average of confidence based on observations
        total_obs = self.observations + other.observations
        new_confidence = ((self.confidence * self.observations + 
                          other.confidence * other.observations) / total_obs)
        
        return TransitionRule(
            condition=self.condition,  # Keep the first rule's condition 
            action=self.action,
            outcome=self.outcome,  # Could merge outcomes more sophisticatedly
            confidence=new_confidence,
            observations=total_obs,
            created_at=min(self.created_at, other.created_at),
            last_updated=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary for serialization."""
        return {
            'condition': asdict(self.condition),
            'action': asdict(self.action), 
            'outcome': asdict(self.outcome),
            'confidence': self.confidence,
            'observations': self.observations,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransitionRule':
        """Create rule from dictionary."""
        return cls(
            condition=StatePattern(**data['condition']),
            action=ActionPattern(**data['action']),
            outcome=StateChange(**data['outcome']),
            confidence=data['confidence'],
            observations=data['observations'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_updated=datetime.fromisoformat(data['last_updated'])
        )


def parse_state_from_text(observation: str) -> StatePattern:
    """Parse game observation text into symbolic state representation."""
    predicates = {}
    
    # Extract location information
    location_match = re.search(r'(?:you are|you\'re) (?:in|at) (?:the )?([^.]+)', observation.lower())
    if location_match:
        predicates['location'] = location_match.group(1).strip()
    
    # Extract inventory items 
    if 'carrying' in observation.lower() or 'inventory' in observation.lower():
        # Look for item patterns after "carrying" or similar
        inventory_text = observation.lower()
        if 'carrying:' in inventory_text:
            inv_part = inventory_text.split('carrying:')[1].split('\n')[0]
            items = [item.strip() for item in inv_part.split(',') if item.strip()]
            predicates['inventory'] = items
        elif 'nothing' in inventory_text and 'carrying' in inventory_text:
            predicates['inventory'] = []
    
    # Extract visible objects/items
    visible_objects = []
    # Look for common object indicators
    object_patterns = [
        r'(?:you can see|there is|you notice) (?:a |an )?([^.]+)',
        r'(?:on the|in the) [^,]+ (?:is|are) (?:a |an )?([^.]+)',
    ]
    
    for pattern in object_patterns:
        matches = re.findall(pattern, observation.lower())
        visible_objects.extend([match.strip() for match in matches])
    
    if visible_objects:
        predicates['visible_objects'] = list(set(visible_objects))
    
    # Extract exit information
    exit_patterns = [
        r'exits?:?\s*([^.]+)',
        r'you can go\s+([^.]+)',
        r'obvious exits?\s*[:\s]+([^.]+)'
    ]
    
    for pattern in exit_patterns:
        exit_match = re.search(pattern, observation.lower())
        if exit_match:
            exits = [exit.strip() for exit in exit_match.group(1).split(',')]
            predicates['exits'] = exits
            break
    
    # Extract NPC information
    npc_patterns = [
        r'([A-Z][a-z]+) (?:is here|stands here|sits here)',
        r'you (?:see|notice) ([A-Z][a-z]+)'
    ]
    
    npcs = []
    for pattern in npc_patterns:
        matches = re.findall(pattern, observation)
        npcs.extend(matches)
    
    if npcs:
        predicates['npcs_present'] = list(set(npcs))
    
    return StatePattern(predicates)


def extract_action_from_command(command: str) -> ActionPattern:
    """Extract action pattern from player command."""
    command = command.lower().strip()
    
    # Common verb patterns
    verb_patterns = {
        r'^(?:go|move|walk|run)\s+(\w+)': ('go', []),
        r'^(?:take|get|pick up)\s+(.+)': ('take', []),
        r'^(?:examine|look at|x)\s+(.+)': ('examine', []),
        r'^(?:use|apply)\s+(.+?)\s+(?:on|with|to)\s+(.+)': ('use', []),
        r'^(?:talk to|speak to|ask)\s+(.+)': ('talk', []),
        r'^(?:open|close)\s+(.+)': ('manipulate', []),
        r'^(?:push|pull|turn)\s+(.+)': ('manipulate', []),
        r'^(?:give|offer)\s+(.+?)\s+to\s+(.+)': ('give', []),
        r'^(?:look|l)$': ('look', []),
        r'^(?:inventory|i)$': ('inventory', []),
    }
    
    for pattern, (verb, _) in verb_patterns.items():
        match = re.match(pattern, command)
        if match:
            groups = match.groups()
            if verb == 'use' and len(groups) == 2:
                return ActionPattern(verb, [groups[0].strip()], [groups[1].strip()])
            elif verb == 'give' and len(groups) == 2:
                return ActionPattern(verb, [groups[0].strip()], [groups[1].strip()])
            elif groups:
                objects = [groups[0].strip()] if groups[0] else []
                return ActionPattern(verb, objects)
            else:
                return ActionPattern(verb, [])
    
    # Default: treat first word as verb, rest as objects
    parts = command.split()
    if parts:
        verb = parts[0]
        objects = parts[1:] if len(parts) > 1 else []
        return ActionPattern(verb, objects)
    
    return ActionPattern('unknown', [command])


def parse_outcome_from_feedback(before_state: StatePattern, after_observation: str, 
                               success_indicators: List[str] = None) -> StateChange:
    """Parse the outcome of an action by comparing before and after states."""
    after_state = parse_state_from_text(after_observation)
    
    additions = {}
    removals = {}
    modifications = {}
    
    # Compare predicates to find changes
    all_keys = set(before_state.predicates.keys()) | set(after_state.predicates.keys())
    
    for key in all_keys:
        before_val = before_state.predicates.get(key)
        after_val = after_state.predicates.get(key)
        
        if before_val is None and after_val is not None:
            additions[key] = after_val
        elif before_val is not None and after_val is None:
            removals[key] = before_val
        elif before_val != after_val:
            modifications[key] = after_val
    
    return StateChange(additions, removals, modifications)
