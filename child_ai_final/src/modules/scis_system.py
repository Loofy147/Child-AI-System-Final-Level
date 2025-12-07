import logging
from datetime import datetime
from core.knowledge_base import KnowledgeBase
from core.logic_engine import LogicEngine
from core.nml_engine import NMLEngine

logger = logging.getLogger(__name__)

class SCISSystem:
    """
    Self-Correction and Integrity System (SCIS).
    Initiative 2: Identifies, diagnoses, and corrects inconsistencies using NML.
    """
    def __init__(self, knowledge_base: KnowledgeBase, logic_engine: LogicEngine):
        self.kb = knowledge_base
        self.logic_engine = logic_engine
        self.nml_engine = NMLEngine()
        self.corrections_count = 0
        self.inconsistency_history = []
        
        # Background monitoring settings
        self.monitoring_enabled = True
        self.last_check_time = None

    def get_corrections_count(self):
        """Returns the total number of self-corrections performed."""
        return self.corrections_count

    def check_for_inconsistencies(self) -> dict:
        """
        Comprehensive consistency auditor using NML.
        Checks for logical contradictions and default rule violations.
        """
        logger.info("SCIS: Starting comprehensive consistency check...")
        self.last_check_time = datetime.now().isoformat()
        
        inconsistencies = []
        facts = self.kb.get_all_facts()
        
        # Check each fact against all other facts for contradictions
        for fact_name, fact_data in facts.items():
            # Check for direct contradictions
            negated_fact = self._negate_fact(fact_name)
            if negated_fact in facts:
                inconsistencies.append({
                    'type': 'direct_contradiction',
                    'fact1': fact_name,
                    'fact2': negated_fact,
                    'certainty1': fact_data['certainty'],
                    'certainty2': facts[negated_fact]['certainty'],
                    'severity': 'high'
                })
        
        # Check for default rule violations using NML
        for fact_name, fact_data in facts.items():
            conflict_analysis = self.nml_engine.check_consistency(
                facts, fact_name, fact_data['certainty']
            )
            
            if conflict_analysis['has_conflicts']:
                for conflict in conflict_analysis['conflicts']:
                    inconsistencies.append({
                        'type': 'nml_conflict',
                        'fact': fact_name,
                        'conflict_details': conflict,
                        'severity': conflict.get('severity', 'medium')
                    })
        
        # Log the results
        if inconsistencies:
            logger.warning(f"SCIS detected {len(inconsistencies)} inconsistencies")
        else:
            logger.info("SCIS: No inconsistencies detected")
        
        return {
            'has_inconsistencies': len(inconsistencies) > 0,
            'inconsistencies': inconsistencies,
            'check_time': self.last_check_time,
            'facts_checked': len(facts)
        }

    def auto_correct_inconsistencies(self) -> dict:
        """
        Automatically corrects detected inconsistencies using NML resolution.
        """
        logger.info("SCIS: Starting automatic correction process...")
        
        check_result = self.check_for_inconsistencies()
        if not check_result['has_inconsistencies']:
            return {
                'status': 'no_corrections_needed',
                'message': 'No inconsistencies detected'
            }
        
        corrections_made = []
        facts = self.kb.get_all_facts()
        
        for inconsistency in check_result['inconsistencies']:
            if inconsistency['type'] == 'direct_contradiction':
                # Resolve direct contradiction by keeping higher certainty fact
                fact1 = inconsistency['fact1']
                fact2 = inconsistency['fact2']
                certainty1 = inconsistency['certainty1']
                certainty2 = inconsistency['certainty2']
                
                if certainty1 > certainty2:
                    # Remove fact2, keep fact1
                    if fact2 in facts:
                        del facts[fact2]
                        self.kb.facts = facts
                        corrections_made.append(f"Removed {fact2} (certainty {certainty2}) in favor of {fact1} (certainty {certainty1})")
                elif certainty2 > certainty1:
                    # Remove fact1, keep fact2
                    if fact1 in facts:
                        del facts[fact1]
                        self.kb.facts = facts
                        corrections_made.append(f"Removed {fact1} (certainty {certainty1}) in favor of {fact2} (certainty {certainty2})")
                else:
                    # Equal certainty - remove both and log for manual review
                    if fact1 in facts:
                        del facts[fact1]
                    if fact2 in facts:
                        del facts[fact2]
                    self.kb.facts = facts
                    corrections_made.append(f"Removed both {fact1} and {fact2} due to equal certainty contradiction")
            
            elif inconsistency['type'] == 'nml_conflict':
                # Use NML engine to resolve the conflict
                conflict_details = inconsistency['conflict_details']
                
                # Create a mock conflict analysis for the NML engine
                mock_analysis = {
                    'has_conflicts': True,
                    'conflicts': [conflict_details],
                    'resolution_strategy': self.nml_engine._generate_resolution_strategy(
                        [conflict_details], 
                        inconsistency['fact'], 
                        facts[inconsistency['fact']]['certainty']
                    )
                }
                
                resolution_result = self.nml_engine.resolve_conflict(mock_analysis, facts)
                self.kb.facts = facts  # Update the knowledge base
                
                if resolution_result['status'] == 'resolved':
                    corrections_made.extend(resolution_result['actions'])
        
        # Update correction count and history
        self.corrections_count += len(corrections_made)
        
        correction_record = {
            'timestamp': datetime.now().isoformat(),
            'corrections_made': corrections_made,
            'inconsistencies_resolved': len(check_result['inconsistencies']),
            'method': 'automatic_nml_resolution'
        }
        
        self.inconsistency_history.append(correction_record)
        
        logger.info(f"SCIS completed automatic correction. Made {len(corrections_made)} corrections.")
        
        return {
            'status': 'corrections_completed',
            'corrections_made': corrections_made,
            'correction_record': correction_record
        }

    def validate_new_fact(self, fact: str, certainty: float, source: str) -> dict:
        """
        Validates a new fact before it's added to the knowledge base.
        Uses NML to check for potential conflicts.
        """
        logger.info(f"SCIS: Validating new fact: {fact} (certainty: {certainty})")
        
        facts = self.kb.get_all_facts()
        conflict_analysis = self.nml_engine.check_consistency(facts, fact, certainty)
        
        if conflict_analysis['has_conflicts']:
            logger.warning(f"SCIS: New fact {fact} would create conflicts")
            return {
                'valid': False,
                'conflicts': conflict_analysis['conflicts'],
                'resolution_strategy': conflict_analysis['resolution_strategy'],
                'recommendation': 'resolve_conflicts_before_adding'
            }
        else:
            logger.info(f"SCIS: New fact {fact} is consistent with knowledge base")
            return {
                'valid': True,
                'message': 'Fact is consistent with existing knowledge base'
            }

    def generate_error_prompt(self, inconsistency: dict) -> str:
        """
        Generates an Error Prompt Mechanism (EPM) message for RL agent feedback.
        """
        if inconsistency['type'] == 'direct_contradiction':
            return f"ERROR: Logical contradiction detected between {inconsistency['fact1']} and {inconsistency['fact2']}. This violates the principle of non-contradiction. Please revise reasoning process."
        
        elif inconsistency['type'] == 'nml_conflict':
            conflict = inconsistency['conflict_details']
            if conflict['type'] == 'default_violation':
                return f"ERROR: Default rule violation detected. Expected {conflict['expected']} but found {conflict['actual']}. Consider if this is a valid exception or an error in reasoning."
        
        return f"ERROR: Inconsistency of type {inconsistency['type']} detected. Please review and correct."

    def get_nml_status(self) -> dict:
        """Returns the current status of the NML engine."""
        return {
            'default_rules_count': len(self.nml_engine.get_default_rules()),
            'exceptions_count': sum(len(exceptions) for exceptions in self.nml_engine.get_exceptions().values()),
            'resolution_history_count': len(self.nml_engine.get_resolution_history()),
            'last_check_time': self.last_check_time
        }

    def _negate_fact(self, fact: str) -> str:
        """Generate the negation of a fact."""
        if fact.startswith("NOT "):
            return fact[4:]  # Remove "NOT "
        else:
            return f"NOT {fact}"

