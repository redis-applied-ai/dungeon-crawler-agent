"""
Prediction Engine: Query-Driven Model Compilation

Compiles relevant rules into executable models for action prediction.
"""

import json
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

from .symbolic_language import TransitionRule, StatePattern, ActionPattern, StateChange
from .transition_model import TransitionModel


@dataclass
class Prediction:
    """Result of predicting an action's outcome."""
    outcome_state: StatePattern
    confidence: float
    reasoning_trace: List[str]
    applied_rules: List[TransitionRule]
    uncertainty_factors: List[str]
    alternative_outcomes: List[Tuple[StatePattern, float]] = None  # (state, probability)
    
    def __post_init__(self):
        if self.alternative_outcomes is None:
            self.alternative_outcomes = []
    
    def to_natural_language(self) -> str:
        """Convert prediction to natural language explanation."""
        explanation = []
        
        if self.confidence > 0.8:
            explanation.append("I'm confident that this action will:")
        elif self.confidence > 0.5:
            explanation.append("I believe this action will likely:")
        else:
            explanation.append("This action might:")
        
        # Describe predicted changes
        changes = []
        for key, value in self.outcome_state.predicates.items():
            if key == 'location':
                changes.append(f"move you to {value}")
            elif key == 'inventory':
                if value:
                    changes.append(f"give you: {', '.join(value)}")
                else:
                    changes.append("empty your inventory")
            elif key == 'visible_objects':
                if value:
                    changes.append(f"reveal: {', '.join(value)}")
        
        if changes:
            explanation.append(f"- {'; '.join(changes)}")
        
        if self.uncertainty_factors:
            explanation.append(f"Uncertain because: {', '.join(self.uncertainty_factors)}")
        
        if self.alternative_outcomes:
            explanation.append("Alternative possibilities:")
            for alt_state, prob in self.alternative_outcomes[:2]:  # Show top 2 alternatives
                explanation.append(f"- ({prob:.1%} chance) Different outcome based on other factors")
        
        return "\n".join(explanation)


class PredictionEngine:
    """Compiles transition models into executable predictors."""
    
    def __init__(self, model: TransitionModel):
        self.model = model
        
    def predict_action_outcome(self, current_state: StatePattern, 
                             proposed_action: ActionPattern) -> Prediction:
        """
        Predict the outcome of taking a proposed action in the current state.
        
        Returns:
            A Prediction object with the expected outcome and confidence.
        """
        # Step 1: Query model for relevant rules
        relevant_rules = self.model.query_relevant_rules(current_state, proposed_action)
        
        if not relevant_rules:
            return self._handle_no_rules(current_state, proposed_action)
        
        # Step 2: Build execution graph from rules
        exec_graph = self._build_transition_graph(relevant_rules, current_state, proposed_action)
        
        # Step 3: Simulate forward through the graph
        predicted_outcome, confidence, reasoning_trace = self._simulate_transition(
            exec_graph, current_state, proposed_action
        )
        
        # Step 4: Identify uncertainty factors
        uncertainty_factors = self._identify_uncertainty_factors(
            relevant_rules, current_state, proposed_action
        )
        
        # Step 5: Generate alternative outcomes
        alternatives = self._generate_alternative_outcomes(
            relevant_rules, current_state, proposed_action
        )
        
        return Prediction(
            outcome_state=predicted_outcome,
            confidence=confidence,
            reasoning_trace=reasoning_trace,
            applied_rules=relevant_rules,
            uncertainty_factors=uncertainty_factors,
            alternative_outcomes=alternatives
        )
    
    def _handle_no_rules(self, current_state: StatePattern, 
                        proposed_action: ActionPattern) -> Prediction:
        """Handle cases where no relevant rules are found."""
        # Use meta-patterns or default assumptions
        default_outcome = current_state  # Assume no change
        uncertainty_factors = ['No prior experience with this action in this state']
        reasoning_trace = ['No matching rules found, assuming no state change']
        
        # Check meta-patterns for general guidance
        for pattern in self.model.meta_patterns.values():
            if self._action_matches_meta_pattern(proposed_action, pattern):
                # Apply meta-pattern heuristics
                reasoning_trace.append(f"Applied meta-pattern: {pattern.description}")
                default_outcome = self._apply_meta_pattern_heuristic(
                    current_state, proposed_action, pattern
                )
                break
        
        return Prediction(
            outcome_state=default_outcome,
            confidence=0.1,  # Very low confidence for unknown actions
            reasoning_trace=reasoning_trace,
            applied_rules=[],
            uncertainty_factors=uncertainty_factors
        )
    
    def _build_transition_graph(self, rules: List[TransitionRule], 
                               current_state: StatePattern, 
                               proposed_action: ActionPattern) -> Dict[str, Any]:
        """Build an execution graph from relevant rules."""
        graph = {
            'primary_rules': [],
            'fallback_rules': [],
            'conditional_rules': [],
            'conflicts': []
        }
        
        for rule in rules:
            # Classify rule based on how well it matches current situation
            match_quality = self._calculate_match_quality(rule, current_state, proposed_action)
            
            if match_quality > 0.9:
                graph['primary_rules'].append(rule)
            elif match_quality > 0.7:
                graph['fallback_rules'].append(rule)
            else:
                graph['conditional_rules'].append(rule)
        
        # Identify conflicts between rules
        conflicts = []
        all_applicable = graph['primary_rules'] + graph['fallback_rules']
        for i, rule1 in enumerate(all_applicable):
            for rule2 in all_applicable[i+1:]:
                if self._rules_have_different_outcomes(rule1, rule2):
                    conflicts.append((rule1, rule2))
        
        graph['conflicts'] = conflicts
        
        return graph
    
    def _simulate_transition(self, exec_graph: Dict[str, Any], 
                           current_state: StatePattern, 
                           proposed_action: ActionPattern) -> Tuple[StatePattern, float, List[str]]:
        """Simulate executing the action using the execution graph."""
        reasoning_trace = []
        
        # Start with primary rules
        primary_rules = exec_graph['primary_rules']
        
        if primary_rules:
            # Use the highest confidence primary rule
            best_rule = max(primary_rules, key=lambda r: r.confidence)
            reasoning_trace.append(f"Applying primary rule: {self._rule_to_string(best_rule)}")
            
            # Apply the rule's outcome to the current state
            predicted_state = best_rule.outcome.apply_to(current_state)
            confidence = best_rule.confidence
            
            # Adjust confidence based on rule age and observation count
            confidence *= self._calculate_temporal_adjustment(best_rule)
            
        elif exec_graph['fallback_rules']:
            # Use fallback rules
            best_rule = max(exec_graph['fallback_rules'], key=lambda r: r.confidence)
            reasoning_trace.append(f"No exact match, using fallback rule: {self._rule_to_string(best_rule)}")
            
            predicted_state = best_rule.outcome.apply_to(current_state)
            confidence = best_rule.confidence * 0.7  # Reduce confidence for fallback
            
        else:
            # Use conditional rules or default behavior
            reasoning_trace.append("No strong matching rules, using best guess")
            predicted_state = current_state  # Default to no change
            confidence = 0.3
        
        # Handle conflicts
        if exec_graph['conflicts']:
            reasoning_trace.append(f"Warning: {len(exec_graph['conflicts'])} rule conflicts detected")
            confidence *= 0.8  # Reduce confidence due to conflicts
        
        return predicted_state, confidence, reasoning_trace
    
    def _calculate_match_quality(self, rule: TransitionRule, 
                               current_state: StatePattern, 
                               proposed_action: ActionPattern) -> float:
        """Calculate how well a rule matches the current situation."""
        # Action similarity
        action_sim = rule.action.similarity(proposed_action)
        
        # State compatibility
        state_compat = self._calculate_state_compatibility(rule.condition, current_state)
        
        # Weight action matching more heavily
        match_quality = 0.7 * action_sim + 0.3 * state_compat
        
        return match_quality
    
    def _calculate_state_compatibility(self, rule_condition: StatePattern, 
                                     current_state: StatePattern) -> float:
        """Calculate how compatible a rule's condition is with the current state."""
        # Count matching predicates vs total predicates in rule condition
        matching_predicates = 0
        total_predicates = len(rule_condition.predicates)
        
        if total_predicates == 0:
            return 1.0  # Universal rule
        
        for key, expected_value in rule_condition.predicates.items():
            if key in current_state.predicates:
                actual_value = current_state.predicates[key]
                
                if isinstance(expected_value, dict) and isinstance(actual_value, dict):
                    # Nested dictionary comparison
                    sub_matches = sum(1 for k, v in expected_value.items() 
                                    if actual_value.get(k) == v)
                    matching_predicates += sub_matches / len(expected_value)
                elif expected_value == actual_value:
                    matching_predicates += 1
                elif isinstance(expected_value, list) and isinstance(actual_value, list):
                    # List overlap
                    overlap = len(set(expected_value) & set(actual_value))
                    total_expected = len(expected_value)
                    matching_predicates += overlap / total_expected if total_expected > 0 else 0
        
        return matching_predicates / total_predicates
    
    def _rules_have_different_outcomes(self, rule1: TransitionRule, rule2: TransitionRule) -> bool:
        """Check if two rules would produce significantly different outcomes."""
        # Compare the outcome state changes
        outcome1_additions = set(rule1.outcome.additions.keys())
        outcome2_additions = set(rule2.outcome.additions.keys())
        
        outcome1_removals = set(rule1.outcome.removals.keys())
        outcome2_removals = set(rule2.outcome.removals.keys())
        
        # If they change different aspects of state, they conflict
        if outcome1_additions != outcome2_additions or outcome1_removals != outcome2_removals:
            return True
        
        # Check if the actual values are different
        for key in outcome1_additions & outcome2_additions:
            if rule1.outcome.additions[key] != rule2.outcome.additions[key]:
                return True
        
        return False
    
    def _calculate_temporal_adjustment(self, rule: TransitionRule) -> float:
        """Adjust confidence based on rule age and observation frequency."""
        from datetime import datetime, timedelta
        
        # More recent rules get slight confidence boost
        age_days = (datetime.now() - rule.last_updated).days
        recency_factor = max(0.8, 1.0 - (age_days * 0.01))  # Slow decay over time
        
        # Rules with more observations are more reliable
        observation_factor = min(1.2, 1.0 + (rule.observations - 1) * 0.05)
        
        return min(1.0, recency_factor * observation_factor)
    
    def _identify_uncertainty_factors(self, rules: List[TransitionRule], 
                                    current_state: StatePattern, 
                                    proposed_action: ActionPattern) -> List[str]:
        """Identify factors that increase uncertainty in the prediction."""
        factors = []
        
        if not rules:
            factors.append("No prior experience with this action")
        
        if len(rules) > 3:
            factors.append("Multiple conflicting rules apply")
        
        # Check for low-confidence rules
        avg_confidence = sum(r.confidence for r in rules) / len(rules) if rules else 0
        if avg_confidence < 0.6:
            factors.append("Low confidence in relevant rules")
        
        # Check for stale rules
        from datetime import datetime, timedelta
        recent_threshold = datetime.now() - timedelta(days=7)
        recent_rules = [r for r in rules if r.last_updated > recent_threshold]
        
        if len(recent_rules) < len(rules) / 2:
            factors.append("Most relevant rules are from older experiences")
        
        # Check for incomplete state information
        required_predicates = set()
        for rule in rules:
            required_predicates.update(rule.condition.predicates.keys())
        
        missing_predicates = required_predicates - set(current_state.predicates.keys())
        if missing_predicates:
            factors.append(f"Missing state information: {', '.join(missing_predicates)}")
        
        return factors
    
    def _generate_alternative_outcomes(self, rules: List[TransitionRule], 
                                     current_state: StatePattern, 
                                     proposed_action: ActionPattern) -> List[Tuple[StatePattern, float]]:
        """Generate alternative outcomes based on conflicting rules."""
        alternatives = []
        
        if len(rules) <= 1:
            return alternatives
        
        # Group rules by similar outcomes
        outcome_groups = defaultdict(list)
        for rule in rules:
            outcome_sig = self._create_outcome_signature(rule.outcome)
            outcome_groups[outcome_sig].append(rule)
        
        # Create alternatives from different outcome groups
        total_confidence = sum(r.confidence for r in rules)
        
        for outcome_sig, group_rules in outcome_groups.items():
            if len(group_rules) > 1:  # Skip single-rule outcomes (already covered)
                continue
                
            rule = group_rules[0]
            alternative_state = rule.outcome.apply_to(current_state)
            probability = rule.confidence / total_confidence if total_confidence > 0 else 0
            
            if probability > 0.1:  # Only include significant alternatives
                alternatives.append((alternative_state, probability))
        
        # Sort by probability
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        return alternatives[:3]  # Return top 3 alternatives
    
    def _create_outcome_signature(self, outcome: StateChange) -> str:
        """Create a signature string for an outcome."""
        # Combine additions, removals, and modifications into a signature
        sig_parts = []
        
        if outcome.additions:
            sig_parts.append(f"add:{json.dumps(outcome.additions, sort_keys=True)}")
        if outcome.removals:
            sig_parts.append(f"rem:{json.dumps(outcome.removals, sort_keys=True)}")
        if outcome.modifications:
            sig_parts.append(f"mod:{json.dumps(outcome.modifications, sort_keys=True)}")
        
        return "|".join(sig_parts)
    
    def _rule_to_string(self, rule: TransitionRule) -> str:
        """Convert a rule to a human-readable string."""
        condition_str = ", ".join(f"{k}={v}" for k, v in rule.condition.predicates.items())
        action_str = f"{rule.action.verb}({', '.join(rule.action.objects)})"
        
        return f"IF {condition_str} THEN {action_str} -> {len(rule.outcome.additions)} changes"
    
    def _action_matches_meta_pattern(self, action: ActionPattern, pattern) -> bool:
        """Check if an action matches a meta-pattern."""
        # Simple matching - could be more sophisticated
        if pattern.pattern_type == 'door_key_pattern':
            return action.verb in ['use', 'unlock'] and \
                   any('door' in obj or 'key' in obj for obj in action.objects + action.targets)
        elif pattern.pattern_type == 'npc_interaction_pattern':
            return action.verb in ['talk', 'ask', 'give'] and len(action.targets) > 0
        
        return False
    
    def _apply_meta_pattern_heuristic(self, current_state: StatePattern, 
                                    action: ActionPattern, pattern) -> StatePattern:
        """Apply meta-pattern heuristics to generate a prediction."""
        # Create a plausible outcome based on the meta-pattern
        new_predicates = current_state.predicates.copy()
        
        if pattern.pattern_type == 'door_key_pattern':
            # Assume door opens if we have the right key
            if 'inventory' in new_predicates:
                # Simple heuristic: if action involves using something on a door
                if action.verb == 'use' and len(action.targets) > 0:
                    new_predicates['last_action'] = f"used {action.objects[0]} on {action.targets[0]}"
        
        elif pattern.pattern_type == 'npc_interaction_pattern':
            # Assume NPC gives information or item
            if action.verb == 'talk':
                new_predicates['last_interaction'] = f"talked to {action.targets[0] if action.targets else 'someone'}"
        
        return StatePattern(new_predicates)