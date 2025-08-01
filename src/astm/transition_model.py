"""
Transition Model: Hierarchical Rule Network

Self-assembling model that builds itself from symbolic transition rules.
"""

import json
from collections import defaultdict
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from .symbolic_language import TransitionRule, StatePattern, ActionPattern, StateChange


@dataclass
class MetaRule:
    """Meta-patterns: rules about rules and general game mechanics."""
    pattern_type: str  # e.g., "door_key_pattern", "npc_interaction_pattern"
    description: str
    conditions: List[str]  # Conditions under which this meta-pattern applies
    confidence: float = 1.0
    examples: List[str] = None  # Rule IDs that exemplify this pattern
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []


class TransitionModel:
    """Hierarchical rule network that self-assembles from experience."""
    
    def __init__(self):
        # Layer 1: Room-specific rules
        self.local_rules: Dict[str, List[TransitionRule]] = defaultdict(list)
        
        # Layer 2: Global patterns (location-independent)
        self.universal_rules: List[TransitionRule] = []
        
        # Layer 3: Meta-patterns
        self.meta_patterns: Dict[str, MetaRule] = {}
        
        # Rule indexing for fast lookup
        self.rules_by_action: Dict[str, List[TransitionRule]] = defaultdict(list)
        self.rules_by_state: Dict[str, List[TransitionRule]] = defaultdict(list)
        
        # Conflict tracking
        self.rule_conflicts: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        
        # Learning statistics
        self.total_rules = 0
        self.successful_predictions = 0
        self.failed_predictions = 0
    
    def integrate_rules(self, new_rules: List[TransitionRule]) -> Dict[str, Any]:
        """
        Integrate new rules into the model, handling merging and conflicts.
        
        Returns:
            Integration statistics and any conflicts found.
        """
        integration_stats = {
            'new_rules_added': 0,
            'rules_merged': 0, 
            'conflicts_detected': 0,
            'meta_patterns_updated': 0
        }
        
        for rule in new_rules:
            result = self._integrate_single_rule(rule)
            for key in integration_stats:
                integration_stats[key] += result.get(key, 0)
        
        # Update meta-patterns based on new rules
        self._update_meta_patterns()
        integration_stats['meta_patterns_updated'] = len(self.meta_patterns)
        
        return integration_stats
    
    def _integrate_single_rule(self, new_rule: TransitionRule) -> Dict[str, int]:
        """Integrate a single rule, handling merging and conflict detection."""
        stats = {'new_rules_added': 0, 'rules_merged': 0, 'conflicts_detected': 0}
        
        # Find similar existing rules
        similar_rules = self._find_similar_rules(new_rule)
        
        if similar_rules:
            # Check if we should merge with the most similar rule
            best_match = max(similar_rules, key=lambda r: self._rule_similarity(new_rule, r))
            similarity = self._rule_similarity(new_rule, best_match)
            
            if similarity > 0.9:  # High similarity - merge
                merged_rule = best_match.merge_with(new_rule)
                self._replace_rule(best_match, merged_rule)
                stats['rules_merged'] = 1
            elif similarity > 0.7:  # Moderate similarity - potential conflict
                self._add_rule(new_rule)
                self._record_conflict(new_rule, best_match)
                stats['new_rules_added'] = 1
                stats['conflicts_detected'] = 1
            else:
                # Low similarity - add as new rule
                self._add_rule(new_rule)
                stats['new_rules_added'] = 1
        else:
            # No similar rules found - add as new
            self._add_rule(new_rule)
            stats['new_rules_added'] = 1
        
        return stats
    
    def _find_similar_rules(self, target_rule: TransitionRule) -> List[TransitionRule]:
        """Find rules similar to the target rule."""
        candidates = []
        
        # Check action-based similarity first (fast filtering)
        action_candidates = self.rules_by_action.get(target_rule.action.verb, [])
        
        for candidate in action_candidates:
            if self._rule_similarity(target_rule, candidate) > 0.5:
                candidates.append(candidate)
        
        return candidates
    
    def _rule_similarity(self, rule1: TransitionRule, rule2: TransitionRule) -> float:
        """Calculate overall similarity between two rules."""
        condition_sim = rule1.condition.similarity(rule2.condition)
        action_sim = rule1.action.similarity(rule2.action)
        
        # Weight condition and action similarity
        return 0.6 * condition_sim + 0.4 * action_sim
    
    def _add_rule(self, rule: TransitionRule):
        """Add a new rule to the appropriate collections."""
        self.total_rules += 1
        rule_id = f"rule_{self.total_rules}"
        
        # Determine if rule is location-specific or universal
        if 'location' in rule.condition.predicates:
            location = rule.condition.predicates['location']
            self.local_rules[location].append(rule)
        else:
            self.universal_rules.append(rule)
        
        # Update indices
        self.rules_by_action[rule.action.verb].append(rule)
        
        # Create state signature for indexing
        state_sig = self._create_state_signature(rule.condition)
        self.rules_by_state[state_sig].append(rule)
    
    def _replace_rule(self, old_rule: TransitionRule, new_rule: TransitionRule):
        """Replace an old rule with a new one in all collections."""
        # Find and replace in local_rules
        for location, rules in self.local_rules.items():
            if old_rule in rules:
                idx = rules.index(old_rule)
                rules[idx] = new_rule
                break
        else:
            # Check universal_rules
            if old_rule in self.universal_rules:
                idx = self.universal_rules.index(old_rule)
                self.universal_rules[idx] = new_rule
        
        # Update indices
        for verb, rules in self.rules_by_action.items():
            if old_rule in rules:
                idx = rules.index(old_rule)
                rules[idx] = new_rule
        
        for state_sig, rules in self.rules_by_state.items():
            if old_rule in rules:
                idx = rules.index(old_rule)
                rules[idx] = new_rule
    
    def _record_conflict(self, rule1: TransitionRule, rule2: TransitionRule):
        """Record a conflict between two rules."""
        rule1_id = id(rule1)
        rule2_id = id(rule2)
        conflict_key = f"{rule1.action.verb}_{self._create_state_signature(rule1.condition)}"
        self.rule_conflicts[conflict_key].append((rule1_id, rule2_id))
    
    def _create_state_signature(self, state: StatePattern) -> str:
        """Create a string signature for a state pattern."""
        # Sort predicates to ensure consistent signatures
        items = sorted(state.predicates.items())
        return json.dumps(items, sort_keys=True)
    
    def query_relevant_rules(self, current_state: StatePattern, 
                           proposed_action: ActionPattern) -> List[TransitionRule]:
        """Find rules relevant to the current state and proposed action."""
        relevant_rules = []
        
        # Get action-based candidates
        action_candidates = self.rules_by_action.get(proposed_action.verb, [])
        
        # Filter by state compatibility
        for rule in action_candidates:
            # Check if rule's condition is compatible with current state
            if self._state_compatible(rule.condition, current_state):
                relevant_rules.append(rule)
        
        # Also check universal rules
        for rule in self.universal_rules:
            if (rule.action.verb == proposed_action.verb and 
                self._state_compatible(rule.condition, current_state)):
                relevant_rules.append(rule)
        
        # Sort by confidence and recency
        relevant_rules.sort(key=lambda r: (r.confidence, r.last_updated), reverse=True)
        
        return relevant_rules
    
    def _state_compatible(self, rule_condition: StatePattern, current_state: StatePattern) -> bool:
        """Check if a rule's condition is compatible with the current state."""
        # Rule is compatible if all its required predicates match the current state
        for key, value in rule_condition.predicates.items():
            if key not in current_state.predicates:
                continue  # Missing predicates are OK (partial matching)
            
            current_value = current_state.predicates[key]
            if isinstance(value, dict) and isinstance(current_value, dict):
                # Check nested dictionaries
                if not all(current_value.get(k) == v for k, v in value.items()):
                    return False
            elif current_value != value:
                return False
        
        return True
    
    def has_state_pattern(self, state: StatePattern) -> bool:
        """Check if the model has seen this state pattern before."""
        state_sig = self._create_state_signature(state)
        return state_sig in self.rules_by_state
    
    def resolve_intersections(self, current_state: StatePattern) -> Dict[str, Any]:
        """Resolve conflicts for rules that apply to the current state."""
        from .conflict_resolver import ConflictResolver
        
        resolver = ConflictResolver()
        resolution_stats = {'conflicts_resolved': 0, 'rules_updated': 0}
        
        # Find all rules that apply to this state
        applicable_rules = []
        for rules in self.local_rules.values():
            for rule in rules:
                if self._state_compatible(rule.condition, current_state):
                    applicable_rules.append(rule)
        
        for rule in self.universal_rules:
            if self._state_compatible(rule.condition, current_state):
                applicable_rules.append(rule)
        
        # Group rules by action for conflict resolution
        rules_by_action = defaultdict(list)
        for rule in applicable_rules:
            rules_by_action[rule.action.verb].append(rule)
        
        # Resolve conflicts within each action group
        for action_verb, rules in rules_by_action.items():
            if len(rules) > 1:
                # Check for conflicts
                conflicting_rules = []
                for i, rule1 in enumerate(rules):
                    for j, rule2 in enumerate(rules[i+1:], i+1):
                        if self._rules_conflict(rule1, rule2):
                            conflicting_rules.extend([rule1, rule2])
                
                if conflicting_rules:
                    # Resolve the conflicts
                    resolved_rule = resolver.resolve_intersections(current_state, conflicting_rules)
                    if resolved_rule:
                        # Replace the first conflicting rule with the resolved one
                        self._replace_rule(conflicting_rules[0], resolved_rule)
                        # Remove the other conflicting rules
                        for rule in conflicting_rules[1:]:
                            self._remove_rule(rule)
                        resolution_stats['conflicts_resolved'] += 1
                        resolution_stats['rules_updated'] += 1
        
        return resolution_stats
    
    def _rules_conflict(self, rule1: TransitionRule, rule2: TransitionRule) -> bool:
        """Check if two rules are in conflict."""
        # Rules conflict if they have similar conditions and actions but different outcomes
        if (rule1.condition.similarity(rule2.condition) > 0.8 and 
            rule1.action.similarity(rule2.action) > 0.8):
            # Check if outcomes are significantly different
            outcome1_sig = self._create_state_signature(StatePattern(rule1.outcome.additions))
            outcome2_sig = self._create_state_signature(StatePattern(rule2.outcome.additions))
            return outcome1_sig != outcome2_sig
        return False
    
    def _remove_rule(self, rule: TransitionRule):
        """Remove a rule from all collections."""
        # Remove from local_rules or universal_rules
        for location, rules in self.local_rules.items():
            if rule in rules:
                rules.remove(rule)
                break
        else:
            if rule in self.universal_rules:
                self.universal_rules.remove(rule)
        
        # Remove from indices
        for verb, rules in self.rules_by_action.items():
            if rule in rules:
                rules.remove(rule)
        
        for state_sig, rules in self.rules_by_state.items():
            if rule in rules:
                rules.remove(rule)
    
    def _update_meta_patterns(self):
        """Update meta-patterns based on current rules."""
        # Analyze rules to identify meta-patterns
        
        # Pattern 1: Door-key relationships
        door_key_rules = []
        for rules in self.local_rules.values():
            for rule in rules:
                if (rule.action.verb in ['use', 'unlock'] and 
                    any('door' in obj or 'key' in obj for obj in rule.action.objects)):
                    door_key_rules.append(rule)
        
        if len(door_key_rules) >= 2:
            self.meta_patterns['door_key_pattern'] = MetaRule(
                pattern_type='door_key_pattern',
                description='Doors typically require specific keys to unlock',
                conditions=['has_key_object', 'has_door_target'],
                confidence=min(1.0, len(door_key_rules) / 5.0),
                examples=[str(id(rule)) for rule in door_key_rules[:3]]
            )
        
        # Pattern 2: NPC interaction patterns
        npc_rules = []
        for rules in self.local_rules.values():
            for rule in rules:
                if rule.action.verb in ['talk', 'ask', 'give'] and rule.action.targets:
                    npc_rules.append(rule)
        
        if len(npc_rules) >= 2:
            self.meta_patterns['npc_interaction_pattern'] = MetaRule(
                pattern_type='npc_interaction_pattern', 
                description='NPCs respond to talk/ask/give actions with information or items',
                conditions=['has_npc_target'],
                confidence=min(1.0, len(npc_rules) / 3.0),
                examples=[str(id(rule)) for rule in npc_rules[:3]]
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get model statistics."""
        total_local_rules = sum(len(rules) for rules in self.local_rules.values())
        
        return {
            'total_rules': self.total_rules,
            'local_rules': total_local_rules,
            'universal_rules': len(self.universal_rules),
            'meta_patterns': len(self.meta_patterns),
            'locations_known': len(self.local_rules),
            'prediction_accuracy': (self.successful_predictions / 
                                  max(1, self.successful_predictions + self.failed_predictions)),
            'total_predictions': self.successful_predictions + self.failed_predictions
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize model to dictionary."""
        return {
            'local_rules': {
                loc: [rule.to_dict() for rule in rules] 
                for loc, rules in self.local_rules.items()
            },
            'universal_rules': [rule.to_dict() for rule in self.universal_rules],
            'meta_patterns': {
                name: asdict(pattern) for name, pattern in self.meta_patterns.items()
            },
            'statistics': self.get_statistics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransitionModel':
        """Deserialize model from dictionary."""
        model = cls()
        
        # Restore local rules
        for location, rule_dicts in data.get('local_rules', {}).items():
            model.local_rules[location] = [
                TransitionRule.from_dict(rule_dict) for rule_dict in rule_dicts
            ]
        
        # Restore universal rules
        model.universal_rules = [
            TransitionRule.from_dict(rule_dict) 
            for rule_dict in data.get('universal_rules', [])
        ]
        
        # Restore meta-patterns
        for name, pattern_dict in data.get('meta_patterns', {}).items():
            model.meta_patterns[name] = MetaRule(**pattern_dict)
        
        # Rebuild indices
        model._rebuild_indices()
        
        return model
    
    def _rebuild_indices(self):
        """Rebuild internal indices after deserialization."""
        self.rules_by_action.clear()
        self.rules_by_state.clear()
        
        all_rules = []
        for rules in self.local_rules.values():
            all_rules.extend(rules)
        all_rules.extend(self.universal_rules)
        
        for rule in all_rules:
            self.rules_by_action[rule.action.verb].append(rule)
            state_sig = self._create_state_signature(rule.condition)
            self.rules_by_state[state_sig].append(rule)