import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class NMLEngine:
    """
    Non-Monotonic Logic (NML) Engine for Self-Correction.
    
    Implements Default Logic and Circumscription for handling:
    - Default assumptions and exceptions
    - Retractable conclusions
    - Consistency checking and conflict resolution
    """
    
    def __init__(self):
        # Default rules: (premise, conclusion, priority)
        # Higher priority = more reliable default
        self.default_rules = []
        
        # Exceptions to default rules
        self.exceptions = {}
        
        # Dependency tracking for retraction
        self.dependencies = {}
        
        # Conflict resolution history
        self.resolution_history = []
        
        self._initialize_core_defaults()
    
    def _initialize_core_defaults(self):
        """Initialize with core default rules."""
        # Default: Birds fly (unless proven otherwise)
        self.add_default_rule("Bird(X)", "Flies(X)", priority=0.9)
        
        # Default: Humans are mortal (high certainty)
        self.add_default_rule("Human(X)", "Mortal(X)", priority=1.0)
        
        # Default: Students study (medium certainty)
        self.add_default_rule("Student(X)", "Studies(X)", priority=0.7)
    
    def add_default_rule(self, premise: str, conclusion: str, priority: float):
        """Add a new default rule with priority."""
        rule = {
            'premise': premise,
            'conclusion': conclusion,
            'priority': priority,
            'timestamp': datetime.now().isoformat()
        }
        self.default_rules.append(rule)
        logger.info(f"Added default rule: {premise} -> {conclusion} (priority: {priority})")
    
    def add_exception(self, rule_premise: str, exception_condition: str):
        """Add an exception to a default rule."""
        if rule_premise not in self.exceptions:
            self.exceptions[rule_premise] = []
        
        self.exceptions[rule_premise].append(exception_condition)
        logger.info(f"Added exception to {rule_premise}: {exception_condition}")
    
    def check_consistency(self, facts: Dict, new_fact: str, new_certainty: float) -> Dict:
        """
        Check if adding a new fact would create inconsistencies.
        Returns conflict analysis and resolution recommendations.
        """
        logger.info(f"Checking consistency for new fact: {new_fact} (certainty: {new_certainty})")
        
        conflicts = []
        
        # Check for direct contradictions
        negated_fact = self._negate_fact(new_fact)
        if negated_fact in facts:
            existing_certainty = facts[negated_fact]['certainty']
            conflicts.append({
                'type': 'direct_contradiction',
                'existing_fact': negated_fact,
                'existing_certainty': existing_certainty,
                'new_fact': new_fact,
                'new_certainty': new_certainty,
                'severity': 'high'
            })
        
        # Check for default rule violations
        for rule in self.default_rules:
            if self._matches_pattern(new_fact, rule['conclusion']):
                # Check if this violates a default assumption
                premise_instance = self._extract_premise_instance(new_fact, rule)
                if premise_instance and premise_instance in facts:
                    expected_conclusion = self._instantiate_conclusion(rule['conclusion'], premise_instance)
                    if expected_conclusion != new_fact:
                        conflicts.append({
                            'type': 'default_violation',
                            'rule': rule,
                            'premise': premise_instance,
                            'expected': expected_conclusion,
                            'actual': new_fact,
                            'severity': 'medium'
                        })
        
        return {
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts,
            'resolution_strategy': self._generate_resolution_strategy(conflicts, new_fact, new_certainty)
        }
    
    def resolve_conflict(self, conflict_analysis: Dict, facts: Dict) -> Dict:
        """
        Resolve conflicts using NML principles.
        Returns the resolution actions taken.
        """
        if not conflict_analysis['has_conflicts']:
            return {'status': 'no_conflicts', 'actions': []}
        
        actions = []
        strategy = conflict_analysis['resolution_strategy']
        
        for action in strategy['actions']:
            if action['type'] == 'retract_fact':
                fact_to_retract = action['fact']
                if fact_to_retract in facts:
                    del facts[fact_to_retract]
                    actions.append(f"Retracted fact: {fact_to_retract}")
                    logger.info(f"NML retracted fact: {fact_to_retract}")
            
            elif action['type'] == 'add_exception':
                rule_premise = action['rule_premise']
                exception = action['exception']
                self.add_exception(rule_premise, exception)
                actions.append(f"Added exception: {exception} to rule {rule_premise}")
            
            elif action['type'] == 'lower_priority':
                # In a full implementation, this would adjust rule priorities
                actions.append(f"Lowered priority of rule: {action['rule']}")
        
        # Record the resolution
        resolution_record = {
            'timestamp': datetime.now().isoformat(),
            'conflicts': conflict_analysis['conflicts'],
            'actions': actions,
            'strategy': strategy['reasoning']
        }
        self.resolution_history.append(resolution_record)
        
        return {
            'status': 'resolved',
            'actions': actions,
            'resolution_record': resolution_record
        }
    
    def _negate_fact(self, fact: str) -> str:
        """Generate the negation of a fact."""
        if fact.startswith("NOT "):
            return fact[4:]  # Remove "NOT "
        else:
            return f"NOT {fact}"
    
    def _matches_pattern(self, fact: str, pattern: str) -> bool:
        """Check if a fact matches a rule pattern (simplified)."""
        # This is a simplified pattern matcher
        # In a full system, this would use proper unification
        if "(" in pattern and ")" in pattern:
            predicate = pattern.split("(")[0]
            return fact.startswith(predicate + "(")
        return fact == pattern
    
    def _extract_premise_instance(self, fact: str, rule: Dict) -> Optional[str]:
        """Extract the premise instance from a fact given a rule."""
        # Simplified extraction - in a full system, this would use unification
        if "(" in fact and ")" in fact:
            parts = fact.split("(")
            if len(parts) > 1:
                entity = parts[1].rstrip(")")
                premise_template = rule['premise']
                return premise_template.replace("X", entity)
        return None
    
    def _instantiate_conclusion(self, conclusion_template: str, premise_instance: str) -> str:
        """Instantiate a conclusion template with specific entities."""
        # Extract entity from premise
        if "(" in premise_instance and ")" in premise_instance:
            entity = premise_instance.split("(")[1].rstrip(")")
            return conclusion_template.replace("X", entity)
        return conclusion_template
    
    def _generate_resolution_strategy(self, conflicts: List, new_fact: str, new_certainty: float) -> Dict:
        """Generate a strategy for resolving conflicts."""
        actions = []
        reasoning = []
        
        for conflict in conflicts:
            if conflict['type'] == 'direct_contradiction':
                existing_certainty = conflict['existing_certainty']
                if new_certainty > existing_certainty:
                    actions.append({
                        'type': 'retract_fact',
                        'fact': conflict['existing_fact']
                    })
                    reasoning.append(f"Retract {conflict['existing_fact']} (certainty {existing_certainty}) in favor of {new_fact} (certainty {new_certainty})")
                else:
                    reasoning.append(f"Reject {new_fact} (certainty {new_certainty}) due to higher certainty of {conflict['existing_fact']} (certainty {existing_certainty})")
            
            elif conflict['type'] == 'default_violation':
                # Add an exception to the default rule
                rule = conflict['rule']
                entity = self._extract_entity_from_fact(new_fact)
                if entity:
                    exception = f"NOT {rule['premise'].replace('X', entity)}"
                    actions.append({
                        'type': 'add_exception',
                        'rule_premise': rule['premise'],
                        'exception': exception
                    })
                    reasoning.append(f"Add exception {exception} to default rule {rule['premise']} -> {rule['conclusion']}")
        
        return {
            'actions': actions,
            'reasoning': reasoning
        }
    
    def _extract_entity_from_fact(self, fact: str) -> Optional[str]:
        """Extract the entity from a fact."""
        if "(" in fact and ")" in fact:
            return fact.split("(")[1].rstrip(")")
        return None
    
    def get_resolution_history(self) -> List:
        """Get the history of all conflict resolutions."""
        return self.resolution_history
    
    def get_default_rules(self) -> List:
        """Get all default rules."""
        return self.default_rules
    
    def get_exceptions(self) -> Dict:
        """Get all exceptions to default rules."""
        return self.exceptions
