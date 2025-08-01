"""
Conflict Resolver: Intersection Resolution & Validation

Handles conflicts between rules and validates rule consistency.
"""

import json
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from .symbolic_language import TransitionRule, StatePattern, ActionPattern, StateChange


@dataclass
class ValidationResult:
    """Result of validating a rule's consistency."""
    is_valid: bool
    logical_conflicts: List[str]
    causal_score: float  # 0.0 to 1.0, higher = more plausible
    meta_consistency: float  # 0.0 to 1.0, consistency with meta-patterns
    warnings: List[str]
    
    @property
    def overall_score(self) -> float:
        """Overall validation score."""
        if not self.is_valid:
            return 0.0
        return (self.causal_score + self.meta_consistency) / 2.0


class ConflictResolver:
    """Resolves conflicts between transition rules and validates consistency."""
    
    def __init__(self, decay_factor: float = 0.95):
        self.decay_factor = decay_factor
        self.resolution_history = []
    
    def resolve_intersections(self, current_state: StatePattern, 
                            conflicting_rules: List[TransitionRule]) -> Optional[TransitionRule]:
        """
        Resolve conflicts between multiple rules that apply to the same situation.
        
        Args:
            current_state: The current state where conflicts arise
            conflicting_rules: List of rules that conflict with each other
            
        Returns:
            A single resolved rule, or None if resolution fails
        """
        if not conflicting_rules:
            return None
        
        if len(conflicting_rules) == 1:
            return conflicting_rules[0]
        
        # Try different resolution strategies
        resolution_strategies = [
            self._confidence_weighted_merger,
            self._temporal_recency_bias,
            self._context_sensitive_selection,
            self._ensemble_prediction
        ]
        
        best_rule = None
        best_score = -1
        
        for strategy in resolution_strategies:
            try:
                resolved_rule = strategy(current_state, conflicting_rules)
                if resolved_rule:
                    validation = self.validate_rule_consistency(resolved_rule)
                    if validation.is_valid and validation.overall_score > best_score:
                        best_rule = resolved_rule
                        best_score = validation.overall_score
            except Exception as e:
                # Strategy failed, try next one
                continue
        
        # Record resolution for learning
        self.resolution_history.append({
            'timestamp': datetime.now(),
            'state_signature': self._create_state_signature(current_state),
            'num_conflicts': len(conflicting_rules),
            'resolution_success': best_rule is not None,
            'final_confidence': best_rule.confidence if best_rule else 0.0
        })
        
        return best_rule
    
    def _confidence_weighted_merger(self, current_state: StatePattern, 
                                  conflicting_rules: List[TransitionRule]) -> TransitionRule:
        """Merge rules using confidence-weighted averaging."""
        # Calculate total weighted confidence
        total_weight = sum(rule.confidence * rule.observations for rule in conflicting_rules)
        
        if total_weight == 0:
            return conflicting_rules[0]  # Fallback
        
        # Use the rule with highest confidence as the base
        base_rule = max(conflicting_rules, key=lambda r: r.confidence)
        
        # Weighted average of outcomes
        merged_additions = {}
        merged_modifications = {}
        merged_removals = {}
        
        # Aggregate outcomes from all rules
        for rule in conflicting_rules:
            weight = (rule.confidence * rule.observations) / total_weight
            
            # Merge additions with weighted voting
            for key, value in rule.outcome.additions.items():
                if key not in merged_additions:
                    merged_additions[key] = {}
                
                if isinstance(value, (str, int, float)):
                    if value not in merged_additions[key]:
                        merged_additions[key][value] = 0
                    merged_additions[key][value] += weight
                else:
                    # For complex values, use first occurrence
                    if 'value' not in merged_additions[key]:
                        merged_additions[key]['value'] = value
                        merged_additions[key]['weight'] = weight
                    elif weight > merged_additions[key]['weight']:
                        merged_additions[key]['value'] = value
                        merged_additions[key]['weight'] = weight
        
        # Convert weighted votes to final values
        final_additions = {}
        for key, candidates in merged_additions.items():
            if 'value' in candidates:
                final_additions[key] = candidates['value']
            else:
                # Choose the candidate with highest weight
                best_candidate = max(candidates.items(), key=lambda x: x[1])
                final_additions[key] = best_candidate[0]
        
        # Similarly for modifications and removals (simplified)
        final_modifications = base_rule.outcome.modifications.copy()
        final_removals = base_rule.outcome.removals.copy()
        
        # Create merged outcome
        merged_outcome = StateChange(
            additions=final_additions,
            modifications=final_modifications,
            removals=final_removals
        )
        
        # Calculate merged confidence
        merged_confidence = total_weight / sum(rule.observations for rule in conflicting_rules)
        merged_confidence = min(1.0, merged_confidence)
        
        return TransitionRule(
            condition=base_rule.condition,
            action=base_rule.action,
            outcome=merged_outcome,
            confidence=merged_confidence,
            observations=sum(rule.observations for rule in conflicting_rules),
            created_at=min(rule.created_at for rule in conflicting_rules),
            last_updated=datetime.now()
        )
    
    def _temporal_recency_bias(self, current_state: StatePattern, 
                             conflicting_rules: List[TransitionRule]) -> TransitionRule:
        """Prioritize more recent rules with recency decay."""
        now = datetime.now()
        
        # Calculate recency weights
        weighted_rules = []
        for rule in conflicting_rules:
            days_old = (now - rule.last_updated).days
            recency_weight = self.decay_factor ** days_old
            weighted_rules.append((rule, recency_weight))
        
        # Select rule with highest recency-adjusted confidence
        best_rule, best_weight = max(weighted_rules, 
                                   key=lambda x: x[0].confidence * x[1])
        
        # Adjust confidence based on recency
        adjusted_confidence = min(1.0, best_rule.confidence * best_weight)
        
        return TransitionRule(
            condition=best_rule.condition,
            action=best_rule.action,
            outcome=best_rule.outcome,
            confidence=adjusted_confidence,
            observations=best_rule.observations,
            created_at=best_rule.created_at,
            last_updated=datetime.now()
        )
    
    def _context_sensitive_selection(self, current_state: StatePattern, 
                                   conflicting_rules: List[TransitionRule]) -> TransitionRule:
        """Select rule based on context similarity to current state."""
        context_scores = []
        
        for rule in conflicting_rules:
            # Calculate how well rule's condition matches current context
            condition_match = self._calculate_context_match(rule.condition, current_state)
            
            # Factor in rule quality
            quality_score = rule.confidence * (1 + rule.observations * 0.1)
            
            # Combined context score
            context_score = condition_match * quality_score
            context_scores.append((rule, context_score))
        
        # Select best context match
        best_rule, best_score = max(context_scores, key=lambda x: x[1])
        
        return best_rule
    
    def _ensemble_prediction(self, current_state: StatePattern, 
                           conflicting_rules: List[TransitionRule]) -> TransitionRule:
        """Create ensemble prediction from multiple rules."""
        # Use voting mechanism for discrete outcomes
        outcome_votes = {}
        confidence_sum = 0
        
        for rule in conflicting_rules:
            outcome_sig = self._create_outcome_signature(rule.outcome)
            weight = rule.confidence * rule.observations
            
            if outcome_sig not in outcome_votes:
                outcome_votes[outcome_sig] = {'rule': rule, 'weight': 0}
            
            outcome_votes[outcome_sig]['weight'] += weight
            confidence_sum += weight
        
        # Select outcome with most votes
        if not outcome_votes:
            return conflicting_rules[0]
        
        best_outcome = max(outcome_votes.items(), key=lambda x: x[1]['weight'])
        winning_rule = best_outcome[1]['rule']
        
        # Calculate ensemble confidence
        ensemble_confidence = best_outcome[1]['weight'] / confidence_sum if confidence_sum > 0 else 0.5
        
        return TransitionRule(
            condition=winning_rule.condition,
            action=winning_rule.action,
            outcome=winning_rule.outcome,
            confidence=min(1.0, ensemble_confidence),
            observations=sum(rule.observations for rule in conflicting_rules),
            created_at=min(rule.created_at for rule in conflicting_rules),
            last_updated=datetime.now()
        )
    
    def validate_rule_consistency(self, rule: TransitionRule) -> ValidationResult:
        """Validate a rule for logical consistency and causal plausibility."""
        logical_conflicts = []
        warnings = []
        
        # Check for logical contradictions
        logical_conflicts.extend(self._check_logical_contradictions(rule))
        
        # Score causal plausibility
        causal_score = self._score_causal_plausibility(rule)
        
        # Check meta-pattern consistency
        meta_consistency = self._check_meta_pattern_consistency(rule)
        
        # Identify warnings
        if rule.confidence < 0.3:
            warnings.append("Very low confidence rule")
        
        if rule.observations == 1:
            warnings.append("Rule based on single observation")
        
        # Rule is valid if no major logical conflicts
        is_valid = len(logical_conflicts) == 0 and causal_score > 0.2
        
        return ValidationResult(
            is_valid=is_valid,
            logical_conflicts=logical_conflicts,
            causal_score=causal_score,
            meta_consistency=meta_consistency,
            warnings=warnings
        )
    
    def _check_logical_contradictions(self, rule: TransitionRule) -> List[str]:
        """Check for logical contradictions in the rule."""
        conflicts = []
        
        # Check if outcome contradicts precondition
        for key, value in rule.outcome.additions.items():
            if key in rule.condition.predicates:
                condition_value = rule.condition.predicates[key]
                if value == condition_value:
                    conflicts.append(f"Outcome adds {key}={value} but it's already required in condition")
        
        # Check for simultaneous addition and removal of same thing
        common_keys = set(rule.outcome.additions.keys()) & set(rule.outcome.removals.keys())
        for key in common_keys:
            conflicts.append(f"Rule both adds and removes {key}")
        
        # Check for impossible state transitions
        if ('location' in rule.outcome.additions and 
            'location' in rule.condition.predicates and
            rule.action.verb not in ['go', 'move', 'teleport', 'fall', 'climb']):
            conflicts.append("Location change without movement action")
        
        return conflicts
    
    def _score_causal_plausibility(self, rule: TransitionRule) -> float:
        """Score how causally plausible a rule is (0.0 to 1.0)."""
        score = 1.0  # Start with full plausibility
        
        # Check action-outcome alignment
        action_verb = rule.action.verb.lower()
        
        # Taking things should add to inventory
        if action_verb in ['take', 'get', 'pick']:
            if 'inventory' not in rule.outcome.additions:
                score *= 0.5  # Reduce plausibility
        
        # Using items might consume them
        if action_verb in ['use', 'apply']:
            if rule.action.objects and 'inventory' not in rule.outcome.removals:
                score *= 0.8  # Slightly suspicious but not impossible
        
        # Movement actions should change location
        if action_verb in ['go', 'move', 'walk']:
            if 'location' not in rule.outcome.additions and 'location' not in rule.outcome.modifications:
                score *= 0.3  # Very suspicious
        
        # Talking shouldn't change physical state much
        if action_verb in ['talk', 'say', 'ask']:
            physical_changes = len([k for k in rule.outcome.additions.keys() 
                                  if k in ['inventory', 'location']])
            if physical_changes > 1:
                score *= 0.6
        
        # Examining things shouldn't change the world
        if action_verb in ['examine', 'look']:
            if len(rule.outcome.additions) > 2:  # Allow some information updates
                score *= 0.4
        
        return max(0.0, min(1.0, score))
    
    def _check_meta_pattern_consistency(self, rule: TransitionRule) -> float:
        """Check consistency with known meta-patterns."""
        # This would ideally check against actual meta-patterns from the model
        # For now, implement basic consistency checks
        
        consistency_score = 1.0
        
        # Door-key pattern consistency
        if (rule.action.verb in ['use', 'unlock'] and 
            any('key' in obj for obj in rule.action.objects) and
            any('door' in target for target in rule.action.targets)):
            
            # Should result in location change or door state change
            if ('location' not in rule.outcome.additions and 
                not any('door' in str(v) for v in rule.outcome.modifications.values())):
                consistency_score *= 0.7
        
        # NPC interaction consistency
        if rule.action.verb in ['talk', 'ask'] and rule.action.targets:
            # Should provide information or items
            if (not rule.outcome.additions and 
                not any('info' in str(v) or 'says' in str(v) for v in rule.outcome.modifications.values())):
                consistency_score *= 0.8
        
        return max(0.0, min(1.0, consistency_score))
    
    def _calculate_context_match(self, rule_condition: StatePattern, 
                               current_state: StatePattern) -> float:
        """Calculate how well rule condition matches current context."""
        # Count overlapping predicates
        common_keys = set(rule_condition.predicates.keys()) & set(current_state.predicates.keys())
        
        if not common_keys:
            return 0.1  # Minimal match for rules with no overlapping context
        
        matching_values = 0
        for key in common_keys:
            rule_value = rule_condition.predicates[key]
            current_value = current_state.predicates[key]
            
            if rule_value == current_value:
                matching_values += 1
            elif isinstance(rule_value, list) and isinstance(current_value, list):
                overlap = len(set(rule_value) & set(current_value))
                total = len(set(rule_value) | set(current_value))
                matching_values += overlap / total if total > 0 else 0
        
        return matching_values / len(common_keys)
    
    def _create_state_signature(self, state: StatePattern) -> str:
        """Create a unique signature for a state pattern."""
        return json.dumps(sorted(state.predicates.items()), sort_keys=True)
    
    def _create_outcome_signature(self, outcome: StateChange) -> str:
        """Create a signature for an outcome."""
        parts = []
        
        if outcome.additions:
            parts.append(f"add:{json.dumps(sorted(outcome.additions.items()), sort_keys=True)}")
        if outcome.removals:
            parts.append(f"rem:{json.dumps(sorted(outcome.removals.items()), sort_keys=True)}")
        if outcome.modifications:
            parts.append(f"mod:{json.dumps(sorted(outcome.modifications.items()), sort_keys=True)}")
        
        return "|".join(parts) if parts else "no_change"
    
    def get_resolution_statistics(self) -> Dict[str, Any]:
        """Get statistics about conflict resolution performance."""
        if not self.resolution_history:
            return {'total_resolutions': 0}
        
        total = len(self.resolution_history)
        successful = sum(1 for r in self.resolution_history if r['resolution_success'])
        
        recent_resolutions = [r for r in self.resolution_history 
                            if (datetime.now() - r['timestamp']).days < 7]
        
        avg_conflicts = sum(r['num_conflicts'] for r in self.resolution_history) / total
        avg_confidence = sum(r['final_confidence'] for r in self.resolution_history 
                           if r['final_confidence'] > 0) / max(1, successful)
        
        return {
            'total_resolutions': total,
            'success_rate': successful / total,
            'recent_resolutions': len(recent_resolutions),
            'avg_conflicts_per_resolution': avg_conflicts,
            'avg_final_confidence': avg_confidence
        }