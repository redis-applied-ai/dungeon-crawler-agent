"""
ASTM Agent: Main integration class that implements the turn-by-turn workflow.

Integrates the ASTM system into the existing dungeon crawler agent.
"""

import json
import logging
import threading
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
    Thread-safe singleton with shared model state.
    """
    
    _instance = None
    _lock = threading.Lock()
    _model_lock = threading.RLock()  # Reentrant lock for nested operations
    
    def __new__(cls, redis_client: Redis, thread_id: str, game_path: str, llm: ChatOpenAI, enable_rule_generation: bool = True, rule_gen_executor=None):
        # Implement singleton pattern for shared instance
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, redis_client: Redis, thread_id: str, game_path: str, llm: ChatOpenAI, enable_rule_generation: bool = True, rule_gen_executor=None):
        # Only initialize once for the singleton
        if self._initialized:
            return
            
        self.redis_client = redis_client
        self.thread_id = thread_id
        self.game_path = game_path
        self.llm = llm
        self.enable_rule_generation = enable_rule_generation
        self.rule_gen_executor = rule_gen_executor
        
        # Initialize ASTM components
        self.model = TransitionModel()
        self.prediction_engine = PredictionEngine(self.model)
        self.conflict_resolver = ConflictResolver()
        
        # State tracking (per-thread state will be managed separately)
        self.current_turn = 0
        
        # Statistics
        self.prediction_accuracy = []
        
        # Load existing model if available
        self._load_model_from_redis()
        
        logger.info(f"ASTM initialized with rule generation {'enabled' if enable_rule_generation else 'disabled'}")
        self._initialized = True
    
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
        
        # Use thread-safe local lock for fast in-memory operations
        with self._model_lock:
            # Track state for this specific turn (thread-local via parameter passing)
            previous_state = getattr(self, '_thread_previous_state', None)
            
            if previous_state and action_for_rules:
                # Only generate rules if there was a significant state change
                # This reduces unnecessary LLM calls for trivial transitions
                state_changed_significantly = self._has_significant_state_change(
                    previous_state, current_state
                )
                
                if state_changed_significantly:
                    # Use feedback if provided, otherwise use the state transition itself as feedback
                    effective_feedback = feedback or f"State transition: {previous_state.predicates} -> {current_state.predicates}"
                    
                    # Generate rules outside the lock to allow parallel rule generation
                    # (the LLM call is the expensive part and doesn't need synchronization)
                    pass  # Will generate rules after releasing lock
                else:
                    logger.debug("No significant state change, skipping rule generation")
                    new_rules = []
            elif not previous_state:
                logger.info("First turn, no previous state for rule generation")
                new_rules = []
            else:
                logger.info("No previous action recorded for rule generation")
                new_rules = []
        
        # Queue rule generation asynchronously (only if enabled) - don't wait for result
        previous_state = getattr(self, '_thread_previous_state', None)
        
        if (self.enable_rule_generation and 
            previous_state and 
            action_for_rules and 
            self._has_significant_state_change(previous_state, current_state)):
            
            # Queue rule generation - don't block current processing
            effective_feedback = feedback or f"State transition: {previous_state.predicates} -> {current_state.predicates}"
            logger.debug(f"Queuing rule generation for action: {action_for_rules.verb}")
            self._queue_rule_generation(
                previous_state, action_for_rules, current_state, effective_feedback
            )
            new_rules = []  # Don't wait for rule generation to complete
        else:
            new_rules = []
            logger.debug(f"Rule generation skipped: enabled={self.enable_rule_generation}, has_prev_state={previous_state is not None}, has_action={action_for_rules is not None}, significant_change=??")
        
        # Always resolve conflicts for current state (fast operation)
        with self._model_lock:
            if self.model.has_state_pattern(current_state):
                resolution_stats = self.model.resolve_intersections(current_state)
                logger.info(f"Resolved intersections: {resolution_stats}")
        
        # Step 4: If we have a proposed action, predict its outcome (outside lock)
        prediction = None
        if proposed_action:
            action_pattern = extract_action_from_command(proposed_action)
            prediction = self.prediction_engine.predict_action_outcome(current_state, action_pattern)
            logger.info(f"Prediction confidence: {prediction.confidence:.2f}")
        
        # Step 5: Update tracking for next turn (thread-local state)
        self._thread_previous_state = current_state
        if proposed_action:
            self.previous_action = extract_action_from_command(proposed_action)
            logger.debug(f"Set previous_action to: {self.previous_action.verb} {self.previous_action.objects}")
        
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
        
        # Use thread-safe local lock for fast in-memory updates
        with self._model_lock:
            self.prediction_accuracy.append(prediction_accuracy)
            
            # Update rule confidences based on accuracy
            for rule in predicted_outcome.applied_rules:
                rule.update_confidence(prediction_accuracy > 0.7)
        
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
        
        Respond with JSON only:
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
        
        Focus on the most important state changes. Be specific about what conditions enabled the action to work. Respond with valid JSON only.
        """
        
        try:
            # Use a faster model for rule generation to reduce latency
            # Rule generation doesn't need the most sophisticated reasoning
            fast_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
            response = fast_llm.invoke([HumanMessage(content=prompt)])
            
            # Debug: log the raw response
            logger.debug(f"LLM response for rule generation: {repr(response.content)}")
            
            if not response.content or not response.content.strip():
                logger.warning("Empty response from LLM for rule generation")
                return []
            
            # Try to extract JSON from response (sometimes wrapped in markdown)
            content = response.content.strip()
            if content.startswith('```json'):
                # Extract JSON from markdown code block
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    content = content[start:end]
            elif not content.startswith('{'):
                # If response doesn't start with {, try to find JSON
                start = content.find('{')
                if start != -1:
                    content = content[start:]
            
            result = json.loads(content)
            
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
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Raw response content: {repr(response.content if 'response' in locals() else 'No response')}")
            
            # Try a simpler prompt with the same model
            simple_prompt = f"""
            Create one simple rule from this game transition in JSON format:
            
            BEFORE: {json.dumps(previous_state.predicates)}
            ACTION: {previous_action.verb} {' '.join(previous_action.objects + previous_action.targets)}
            AFTER: {json.dumps(current_state.predicates)}
            
            Return only this JSON:
            {{"rules": [{{"condition": {{}}, "action": {{"verb": "", "objects": [], "targets": []}}, "outcome": {{"additions": {{}}, "removals": {{}}, "modifications": {{}}}}, "confidence": 0.7}}]}}
            """
            
            try:
                simple_response = fast_llm.invoke([HumanMessage(content=simple_prompt)])
                if simple_response.content and simple_response.content.strip():
                    simple_result = json.loads(simple_response.content.strip())
                    logger.info("Successfully generated rule with simplified prompt")
                    
                    rules = []
                    for rule_data in simple_result.get('rules', []):
                        try:
                            condition = StatePattern(rule_data.get('condition', {}))
                            action = ActionPattern(
                                verb=rule_data.get('action', {}).get('verb', previous_action.verb),
                                objects=rule_data.get('action', {}).get('objects', previous_action.objects),
                                targets=rule_data.get('action', {}).get('targets', previous_action.targets)
                            )
                            outcome = StateChange(
                                additions=rule_data.get('outcome', {}).get('additions', {}),
                                removals=rule_data.get('outcome', {}).get('removals', {}),
                                modifications=rule_data.get('outcome', {}).get('modifications', {})
                            )
                            
                            rule = TransitionRule(
                                condition=condition,
                                action=action,
                                outcome=outcome,
                                confidence=rule_data.get('confidence', 0.5),
                                observations=1
                            )
                            rules.append(rule)
                        except Exception as inner_e:
                            logger.warning(f"Failed to parse simplified rule: {inner_e}")
                            continue
                    
                    if rules:
                        return rules
                        
            except Exception as simple_e:
                logger.error(f"Simplified prompt also failed: {simple_e}")
            
            # Final fallback: create simple rule based on observed changes
            outcome = parse_outcome_from_feedback(previous_state, 
                                                json.dumps(current_state.predicates))
            
            fallback_rule = TransitionRule(
                condition=previous_state,
                action=previous_action,
                outcome=outcome,
                confidence=0.3,  # Lower confidence for fallback
                observations=1
            )
            
            logger.info("Using fallback rule generation")
            return [fallback_rule]
            
        except Exception as e:
            logger.error(f"Failed to generate rules with LLM: {e}")
            
            # Fallback: create simple rule based on observed changes
            outcome = parse_outcome_from_feedback(previous_state, 
                                                json.dumps(current_state.predicates))
            
            fallback_rule = TransitionRule(
                condition=previous_state,
                action=previous_action,
                outcome=outcome,
                confidence=0.3,  # Lower confidence for fallback
                observations=1
            )
            
            return [fallback_rule]
    
    def _queue_rule_generation(self, previous_state: StatePattern, previous_action: ActionPattern,
                              current_state: StatePattern, feedback: str):
        """Queue rule generation in background - don't block current processing."""
        if not self.rule_gen_executor:
            logger.warning("No rule generation executor available, generating rules synchronously")
            # Fallback to synchronous generation
            new_rules = self._generate_transition_rules(previous_state, previous_action, current_state, feedback)
            with self._model_lock:
                if new_rules:
                    integration_stats = self.model.integrate_rules(new_rules)
                    logger.info(f"Integrated {len(new_rules)} new rules: {integration_stats}")
            return
        
        def generate_and_integrate():
            try:
                logger.debug(f"Background rule generation started for action: {previous_action.verb}")
                new_rules = self._generate_transition_rules(previous_state, previous_action, current_state, feedback)
                
                # Integrate rules with lock
                with self._model_lock:
                    if new_rules:
                        integration_stats = self.model.integrate_rules(new_rules)
                        logger.info(f"Background: Integrated {len(new_rules)} new rules: {integration_stats}")
                    else:
                        logger.debug("Background: No rules generated from LLM")
                        
            except Exception as e:
                logger.error(f"💥 Background rule generation failed: {e}")
        
        # Submit to background executor - don't wait for result
        self.rule_gen_executor.submit(generate_and_integrate)
        logger.debug(f"Rule generation queued in background for action: {previous_action.verb}")
    
    def _has_significant_state_change(self, previous_state: StatePattern, 
                                     current_state: StatePattern) -> bool:
        """Check if state change is significant enough to warrant rule generation."""
        prev_predicates = previous_state.predicates
        curr_predicates = current_state.predicates
        
        # Significant keys that indicate important state changes
        significant_keys = {'location', 'inventory', 'score', 'visible_objects', 'npcs_present', 'exits'}
        
        # Check if any significant keys changed
        for key in significant_keys:
            prev_value = prev_predicates.get(key)
            curr_value = curr_predicates.get(key)
            
            # Convert lists to tuples for comparison (to handle unhashable types)
            if isinstance(prev_value, list):
                prev_value = tuple(sorted(prev_value)) if prev_value else None
            if isinstance(curr_value, list):
                curr_value = tuple(sorted(curr_value)) if curr_value else None
                
            if prev_value != curr_value:
                return True
        
        # Check if new keys appeared or old keys disappeared
        prev_keys = set(prev_predicates.keys())
        curr_keys = set(curr_predicates.keys())
        
        # Significant if keys were added/removed
        if prev_keys != curr_keys:
            return True
        
        # Count total changed predicates (non-significant keys)
        changed_count = 0
        for key in prev_keys & curr_keys:  # Keys present in both
            if key not in significant_keys:
                prev_value = prev_predicates[key]
                curr_value = curr_predicates[key]
                
                # Handle list comparison
                if isinstance(prev_value, list):
                    prev_value = tuple(sorted(prev_value)) if prev_value else None
                if isinstance(curr_value, list):
                    curr_value = tuple(sorted(curr_value)) if curr_value else None
                    
                if prev_value != curr_value:
                    changed_count += 1
        
        # Significant if more than 2 non-significant predicates changed
        return changed_count > 2
    
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
    
    def save_model_to_redis_final(self):
        """Save model to Redis at end of game with proper locking."""
        # Use Redis lock for final save to prevent conflicts with other game instances
        redis_lock = Lock(self.redis_client, self.get_lock_key(), timeout=30)
        
        with redis_lock:
            with self._model_lock:
                logger.info(f"Final save: ASTM model with {len(self.model.rules) if hasattr(self.model, 'rules') else 'unknown'} rules")
                self._save_model_to_redis()
    
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
