"""
ASTM Agent: Main integration class that implements the turn-by-turn workflow.

Integrates the ASTM system into the existing dungeon crawler agent.
"""

import json
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import asdict
from datetime import datetime

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from redis import Redis
from redis.lock import Lock

from .symbolic_language import (
    TransitionRule, StatePattern, ActionPattern, StateChange,
    parse_state_from_text, extract_action_from_command, parse_outcome_from_feedback
)
from .transition_model import TransitionModel
from .prediction_engine import PredictionEngine, Prediction
from .conflict_resolver import ConflictResolver


logger = logging.getLogger(__name__)


class ASTMAgent:
    """
    Adaptive Symbolic Transition Modeling Agent
    
    Implements the self-assembling predictive modeling system.
    """
    
    def __init__(self, redis_client: Redis, thread_id: str, game_path: str, llm: ChatOpenAI):
        self.redis_client = redis_client
        self.thread_id = thread_id
        self.game_path = game_path
        self.llm = llm
        
        # Initialize ASTM components
        self.model = TransitionModel()
        self.prediction_engine = PredictionEngine(self.model)
        self.conflict_resolver = ConflictResolver()
        
        # State tracking
        self.previous_state = None
        self.previous_action = None
        self.current_turn = 0
        
        # Statistics
        self.prediction_accuracy = []
        
        # Load existing model if available
        self._load_model_from_redis()
    
    def process_turn(self, observation: str, feedback: str = None, 
                    proposed_action: str = None, executed_action: str = None) -> Dict[str, Any]:
        """
        Process a single turn with ASTM workflow.
        
        Args:
            observation: Current game observation text
            feedback: Feedback from previous action (if any)
            proposed_action: Action the agent is considering for next turn
            executed_action: Action that was just executed (for rule generation)
            
        Returns:
            Dictionary with prediction, recommended action, and ASTM analysis
        """
        self.current_turn += 1
        logger.info(f"ASTM Turn {self.current_turn}: Processing observation")
        
        # Step 1: Parse current state from observation
        current_state = parse_state_from_text(observation)
        logger.debug(f"Parsed state: {current_state.predicates}")
        
        # Step 2: Generate/update symbolic rules from this turn
        new_rules = []
        
        # Use executed_action if provided, otherwise fall back to self.previous_action
        action_for_rules = None
        if executed_action:
            action_for_rules = extract_action_from_command(executed_action)
            logger.debug(f"Using executed_action for rules: {executed_action}")
        elif self.previous_action:
            action_for_rules = self.previous_action
            logger.debug(f"Using stored previous_action for rules: {self.previous_action}")
        
        # Use Redis lock to prevent race conditions when updating model
        # Block until we can acquire the lock - this is critical data
        lock = Lock(self.redis_client, self.get_lock_key(), timeout=30)
        
        with lock:
            # Reload model from Redis to get latest state
            self._load_model_from_redis()
            
            if self.previous_state and action_for_rules:
                # Use feedback if provided, otherwise use the state transition itself as feedback
                effective_feedback = feedback or f"State transition: {self.previous_state.predicates} -> {current_state.predicates}"
                
                new_rules = self._generate_transition_rules(
                    self.previous_state, action_for_rules, current_state, effective_feedback
                )
                
                if new_rules:
                    integration_stats = self.model.integrate_rules(new_rules)
                    logger.info(f"Integrated {len(new_rules)} new rules: {integration_stats}")
                else:
                    logger.info("No rules generated from transition")
            elif not self.previous_state:
                logger.info("First turn, no previous state for rule generation")
                new_rules = []
            else:
                logger.info("No previous action recorded for rule generation")
                new_rules = []
            
            # Step 3: Resolve conflicts if agent returns to known state  
            if self.model.has_state_pattern(current_state):
                resolution_stats = self.model.resolve_intersections(current_state)
                logger.info(f"Resolved intersections: {resolution_stats}")
            
            # Step 6: Save updated model state
            self._save_model_to_redis()
        
        # Step 4: If we have a proposed action, predict its outcome (outside lock)
        prediction = None
        if proposed_action:
            action_pattern = extract_action_from_command(proposed_action)
            prediction = self.prediction_engine.predict_action_outcome(current_state, action_pattern)
            logger.info(f"Prediction confidence: {prediction.confidence:.2f}")
        
        # Step 5: Update tracking for next turn
        self.previous_state = current_state
        if proposed_action:
            self.previous_action = extract_action_from_command(proposed_action)
            logger.debug(f"Set previous_action to: {self.previous_action}")
        
        return {
            'current_state': current_state,
            'new_rules_generated': len(new_rules),
            'model_stats': self.model.get_statistics(),
            'prediction': prediction,
            'astm_analysis': self._generate_analysis_report()
        }
    
    def get_action_prediction(self, observation: str, proposed_action: str) -> Prediction:
        """
        Get a prediction for a proposed action without updating the model.
        
        Args:
            observation: Current game observation
            proposed_action: Action to predict
            
        Returns:
            Prediction object with expected outcome
        """
        current_state = parse_state_from_text(observation)
        action_pattern = extract_action_from_command(proposed_action)
        
        return self.prediction_engine.predict_action_outcome(current_state, action_pattern)
    
    def validate_prediction(self, predicted_outcome: Prediction, actual_outcome: str) -> Dict[str, Any]:
        """
        Validate a prediction against actual outcome and update statistics.
        
        Args:
            predicted_outcome: Previous prediction
            actual_outcome: Actual result text
            
        Returns:
            Validation statistics
        """
        # Parse actual outcome
        actual_state = parse_state_from_text(actual_outcome)
        
        # Compare predicted vs actual
        prediction_accuracy = self._calculate_prediction_accuracy(
            predicted_outcome.outcome_state, actual_state
        )
        
        # Use Redis lock for updating prediction statistics and rule confidences
        # Block until we can acquire the lock - this data is important for model accuracy
        lock = Lock(self.redis_client, self.get_lock_key(), timeout=30)
        
        with lock:
            # Reload model to get latest state
            self._load_model_from_redis()
            
            self.prediction_accuracy.append(prediction_accuracy)
            
            # Update rule confidences based on accuracy
            for rule in predicted_outcome.applied_rules:
                rule.update_confidence(prediction_accuracy > 0.7)
            
            # Save updated statistics
            self._save_model_to_redis()
        
        return {
            'prediction_accuracy': prediction_accuracy,
            'overall_accuracy': sum(self.prediction_accuracy) / len(self.prediction_accuracy),
            'total_predictions': len(self.prediction_accuracy)
        }
    
    def _generate_transition_rules(self, previous_state: StatePattern, previous_action: ActionPattern,
                                 current_state: StatePattern, feedback: str) -> List[TransitionRule]:
        """Generate transition rules from experience using LLM."""
        
        # Create prompt for rule generation
        prompt = f"""
        You are analyzing a text-based game transition to create symbolic rules.
        
        BEFORE STATE: {json.dumps(previous_state.predicates, indent=2)}
        ACTION TAKEN: {previous_action.verb} {' '.join(previous_action.objects)} {' '.join(previous_action.targets)}
        AFTER STATE: {json.dumps(current_state.predicates, indent=2)}
        FEEDBACK: {feedback}
        
        Generate 1-3 symbolic transition rules from this experience. Each rule should be:
        - A condition (what state was required)
        - An action (what was done)  
        - An outcome (what changed)
        - A confidence (0.0-1.0 based on how reliable this seems)
        
        Format as JSON:
        {{
            "rules": [
                {{
                    "condition": {{"location": "kitchen", "has_item": "key"}},
                    "action": {{"verb": "use", "objects": ["key"], "targets": ["door"]}},
                    "outcome": {{
                        "additions": {{"location": "garden"}},
                        "removals": {{"has_item": "key"}},
                        "modifications": {{}}
                    }},
                    "confidence": 0.9,
                    "reasoning": "Using key on door typically opens it"
                }}
            ]
        }}
        
        Focus on the most important state changes. Be specific about what conditions enabled the action to work.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = json.loads(response.content)
            
            rules = []
            for rule_data in result.get('rules', []):
                try:
                    # Convert JSON to TransitionRule objects
                    condition = StatePattern(rule_data['condition'])
                    action = ActionPattern(
                        verb=rule_data['action'].get('verb', ''),
                        objects=rule_data['action'].get('objects', []),
                        targets=rule_data['action'].get('targets', [])
                    )
                    outcome = StateChange(
                        additions=rule_data['outcome'].get('additions', {}),
                        removals=rule_data['outcome'].get('removals', {}), 
                        modifications=rule_data['outcome'].get('modifications', {})
                    )
                    
                    rule = TransitionRule(
                        condition=condition,
                        action=action,
                        outcome=outcome,
                        confidence=rule_data['confidence'],
                        observations=1
                    )
                    
                    rules.append(rule)
                    logger.debug(f"Generated rule: {rule_data.get('reasoning', 'No reasoning')}")
                    
                except (KeyError, ValueError) as e:
                    logger.warning(f"Failed to parse rule: {e}")
                    continue
            
            return rules
            
        except Exception as e:
            logger.error(f"Failed to generate rules with LLM: {e}")
            
            # Fallback: create simple rule based on observed changes
            outcome = parse_outcome_from_feedback(previous_state, 
                                                json.dumps(current_state.predicates))
            
            fallback_rule = TransitionRule(
                condition=previous_state,
                action=previous_action,
                outcome=outcome,
                confidence=0.5,  # Lower confidence for fallback
                observations=1
            )
            
            return [fallback_rule]
    
    def _calculate_prediction_accuracy(self, predicted_state: StatePattern, 
                                     actual_state: StatePattern) -> float:
        """Calculate how accurate a prediction was."""
        predicted_predicates = set(predicted_state.predicates.items())
        actual_predicates = set(actual_state.predicates.items())
        
        if not predicted_predicates and not actual_predicates:
            return 1.0  # Both empty = perfect match
        
        total_predicates = predicted_predicates | actual_predicates
        matching_predicates = predicted_predicates & actual_predicates
        
        return len(matching_predicates) / len(total_predicates) if total_predicates else 0.0
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate an analysis report of current ASTM state."""
        stats = self.model.get_statistics()
        resolver_stats = self.conflict_resolver.get_resolution_statistics()
        
        accuracy = (sum(self.prediction_accuracy) / len(self.prediction_accuracy) 
                   if self.prediction_accuracy else 0.0)
        
        return {
            'model_statistics': stats,
            'conflict_resolution': resolver_stats,
            'prediction_accuracy': accuracy,
            'turns_processed': self.current_turn,
            'meta_patterns': list(self.model.meta_patterns.keys()),
            'locations_learned': len(self.model.local_rules),
        }
    
    def get_memory_key(self) -> str:
        """Get Redis key for storing ASTM model."""
        return f"astm_model:{self.thread_id}:{self.game_path}"
    
    def get_lock_key(self) -> str:
        """Get Redis key for ASTM model lock."""
        return f"astm_lock:{self.thread_id}:{self.game_path}"
    
    def _save_model_to_redis(self):
        """Save current model state to Redis."""
        key = self.get_memory_key()
        
        model_data = {
            'model': self.model.to_dict(),
            'current_turn': self.current_turn,
            'prediction_accuracy': self.prediction_accuracy,
            'saved_at': datetime.now().isoformat()
        }
        
        try:
            self.redis_client.json().set(key, "$", model_data)
            logger.debug("Saved ASTM model to Redis")
        except Exception as e:
            logger.error(f"Failed to save ASTM model: {e}")
    
    def _load_model_from_redis(self):
        """Load existing model state from Redis."""
        key = self.get_memory_key()
        
        try:
            model_data = self.redis_client.json().get(key)
            if model_data:
                self.model = TransitionModel.from_dict(model_data['model'])
                self.prediction_engine = PredictionEngine(self.model)
                self.current_turn = model_data.get('current_turn', 0)
                self.prediction_accuracy = model_data.get('prediction_accuracy', [])
                
                logger.info(f"Loaded existing ASTM model with {self.model.total_rules} rules")
            else:
                logger.info("No existing ASTM model found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load ASTM model: {e}")
    
    def get_model_summary(self) -> str:
        """Get a human-readable summary of the current model."""
        stats = self.model.get_statistics()
        accuracy = (sum(self.prediction_accuracy) / len(self.prediction_accuracy) 
                   if self.prediction_accuracy else 0.0)
        
        summary = f"""
ASTM Model Summary (Turn {self.current_turn}):
- Total Rules: {stats['total_rules']}
- Locations Learned: {stats['locations_known']}
- Universal Rules: {stats['universal_rules']}
- Meta-Patterns: {stats['meta_patterns']}
- Prediction Accuracy: {accuracy:.1%} ({len(self.prediction_accuracy)} predictions)
- Model Accuracy: {stats['prediction_accuracy']:.1%}

Recent Performance:
- Rules by Location: {dict(list(self.model.local_rules.items())[:3])} (showing first 3)
- Meta-Patterns: {list(self.model.meta_patterns.keys())}
        """
        
        return summary.strip()
    
    def suggest_exploration_actions(self, current_observation: str) -> List[str]:
        """Suggest actions that would help improve the model."""
        current_state = parse_state_from_text(current_observation)
        suggestions = []
        
        # Suggest examining unknown objects
        if 'visible_objects' in current_state.predicates:
            for obj in current_state.predicates['visible_objects']:
                # Check if we have rules about examining this object
                examine_action = ActionPattern('examine', [obj])
                relevant_rules = self.model.query_relevant_rules(current_state, examine_action)
                
                if not relevant_rules:
                    suggestions.append(f"examine {obj}")
        
        # Suggest talking to unknown NPCs
        if 'npcs_present' in current_state.predicates:
            for npc in current_state.predicates['npcs_present']:
                talk_action = ActionPattern('talk', [], [npc])
                relevant_rules = self.model.query_relevant_rules(current_state, talk_action)
                
                if not relevant_rules:
                    suggestions.append(f"talk to {npc}")
        
        # Suggest trying exits we haven't explored
        if 'exits' in current_state.predicates:
            for exit in current_state.predicates['exits']:
                go_action = ActionPattern('go', [exit])
                relevant_rules = self.model.query_relevant_rules(current_state, go_action)
                
                if len(relevant_rules) < 2:  # Few rules = uncertain outcome
                    suggestions.append(f"go {exit}")
        
        return suggestions[:3]  # Return top 3 suggestions
