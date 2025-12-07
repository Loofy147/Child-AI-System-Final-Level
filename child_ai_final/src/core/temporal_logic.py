import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class TemporalLogicEngine:
    """
    Temporal Logic (TL) Engine for Lifelong Learning and Policy Tracking.
    
    Implements Linear Temporal Logic (LTL) for:
    - Policy version tracking and evolution
    - Temporal reasoning about knowledge changes
    - Catastrophic forgetting prevention
    - Performance trend analysis
    """
    
    def __init__(self):
        # Policy history with temporal annotations
        self.policy_timeline = []
        
        # Knowledge evolution tracking
        self.knowledge_timeline = []
        
        # Performance metrics over time
        self.performance_timeline = []
        
        # Temporal constraints and invariants
        self.temporal_constraints = []
        
        # Forgetting prevention mechanisms
        self.critical_knowledge = {}
        
        self._initialize_temporal_framework()
    
    def _initialize_temporal_framework(self):
        """Initialize the temporal logic framework with core constraints."""
        # Core temporal constraint: Performance should not degrade significantly
        self.add_temporal_constraint(
            "ALWAYS (performance_drop > 0.2 -> trigger_knowledge_consolidation)",
            priority=1.0,
            description="Prevent catastrophic forgetting"
        )
        
        # Policy evolution constraint: New policies should build on previous ones
        self.add_temporal_constraint(
            "ALWAYS (new_policy -> EVENTUALLY improved_performance)",
            priority=0.9,
            description="Ensure policy evolution leads to improvement"
        )
        
        logger.info("Temporal Logic Engine initialized with core constraints")
    
    def add_temporal_constraint(self, ltl_formula: str, priority: float, description: str):
        """Add a new temporal logic constraint."""
        constraint = {
            'formula': ltl_formula,
            'priority': priority,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'violations': 0
        }
        self.temporal_constraints.append(constraint)
        logger.info(f"Added temporal constraint: {description}")
    
    def record_policy_update(self, policy_version: str, scenario: str, performance: float, 
                           changes: Dict, metadata: Dict = None) -> str:
        """Record a policy update in the temporal timeline."""
        timestamp = datetime.now().isoformat()
        
        policy_record = {
            'timestamp': timestamp,
            'policy_version': policy_version,
            'scenario': scenario,
            'performance': performance,
            'changes': changes,
            'metadata': metadata or {},
            'previous_version': self.policy_timeline[-1]['policy_version'] if self.policy_timeline else None
        }
        
        self.policy_timeline.append(policy_record)
        
        # Check for performance degradation (catastrophic forgetting indicator)
        if len(self.policy_timeline) > 1:
            previous_performance = self.policy_timeline[-2]['performance']
            performance_drop = previous_performance - performance
            
            if performance_drop > 0.2:  # Significant degradation threshold
                logger.warning(f"Significant performance drop detected: {performance_drop:.3f}")
                self._trigger_knowledge_consolidation(policy_record)
        
        logger.info(f"Recorded policy update: {policy_version} (performance: {performance:.3f})")
        return timestamp
    
    def record_knowledge_change(self, change_type: str, entity: str, old_value: any, 
                              new_value: any, source: str) -> str:
        """Record a knowledge base change in the temporal timeline."""
        timestamp = datetime.now().isoformat()
        
        knowledge_record = {
            'timestamp': timestamp,
            'change_type': change_type,  # 'add', 'update', 'remove'
            'entity': entity,
            'old_value': old_value,
            'new_value': new_value,
            'source': source
        }
        
        self.knowledge_timeline.append(knowledge_record)
        
        # Mark as critical knowledge if it's frequently referenced
        if change_type in ['add', 'update']:
            self._evaluate_knowledge_criticality(entity, new_value)
        
        logger.info(f"Recorded knowledge change: {change_type} {entity}")
        return timestamp
    
    def check_temporal_constraints(self) -> Dict:
        """Check all temporal constraints against the current timeline."""
        violations = []
        
        for constraint in self.temporal_constraints:
            violation = self._evaluate_ltl_constraint(constraint)
            if violation:
                violations.append(violation)
                constraint['violations'] += 1
        
        return {
            'has_violations': len(violations) > 0,
            'violations': violations,
            'constraints_checked': len(self.temporal_constraints)
        }
    
    def _evaluate_ltl_constraint(self, constraint: Dict) -> Optional[Dict]:
        """Evaluate a single LTL constraint (simplified implementation)."""
        formula = constraint['formula']
        
        # Simplified LTL evaluation for key patterns
        if "performance_drop > 0.2" in formula and len(self.policy_timeline) >= 2:
            recent_performances = [p['performance'] for p in self.policy_timeline[-5:]]
            if len(recent_performances) >= 2:
                max_drop = max(recent_performances[i] - recent_performances[i+1] 
                             for i in range(len(recent_performances)-1))
                if max_drop > 0.2:
                    return {
                        'constraint': constraint,
                        'violation_type': 'performance_degradation',
                        'severity': 'high',
                        'details': f"Performance drop of {max_drop:.3f} detected"
                    }
        
        if "EVENTUALLY improved_performance" in formula and len(self.policy_timeline) >= 3:
            # Check if recent policy changes led to improvement within reasonable time
            recent_policies = self.policy_timeline[-3:]
            if len(recent_policies) >= 3:
                initial_perf = recent_policies[0]['performance']
                final_perf = recent_policies[-1]['performance']
                if final_perf <= initial_perf:
                    return {
                        'constraint': constraint,
                        'violation_type': 'no_improvement',
                        'severity': 'medium',
                        'details': f"No performance improvement over {len(recent_policies)} policy updates"
                    }
        
        return None
    
    def _trigger_knowledge_consolidation(self, policy_record: Dict):
        """Trigger knowledge consolidation to prevent catastrophic forgetting."""
        logger.info("Triggering knowledge consolidation due to performance degradation")
        
        # Identify critical knowledge that should be preserved
        critical_facts = self._identify_critical_knowledge()
        
        # Create consolidation record
        consolidation_record = {
            'timestamp': datetime.now().isoformat(),
            'trigger': 'performance_degradation',
            'policy_version': policy_record['policy_version'],
            'critical_knowledge_preserved': len(critical_facts),
            'consolidation_strategy': 'elastic_weight_consolidation'  # Placeholder
        }
        
        # In a full implementation, this would:
        # 1. Apply EWC (Elastic Weight Consolidation) to neural components
        # 2. Strengthen synaptic connections for critical knowledge
        # 3. Adjust learning rates for different knowledge domains
        
        return consolidation_record
    
    def _identify_critical_knowledge(self) -> List[str]:
        """Identify knowledge that is critical and should not be forgotten."""
        critical_facts = []
        
        # Knowledge that appears frequently in successful reasoning chains
        for entity, metadata in self.critical_knowledge.items():
            if metadata.get('usage_frequency', 0) > 5:
                critical_facts.append(entity)
        
        # Knowledge with high certainty from reliable sources
        # (This would integrate with the knowledge base in a full implementation)
        
        return critical_facts
    
    def _evaluate_knowledge_criticality(self, entity: str, value: any):
        """Evaluate and update the criticality of a knowledge entity."""
        if entity not in self.critical_knowledge:
            self.critical_knowledge[entity] = {
                'usage_frequency': 0,
                'last_accessed': datetime.now().isoformat(),
                'importance_score': 0.5
            }
        
        # Update usage frequency (simplified)
        self.critical_knowledge[entity]['usage_frequency'] += 1
        self.critical_knowledge[entity]['last_accessed'] = datetime.now().isoformat()
        
        # Calculate importance score based on usage and recency
        frequency = self.critical_knowledge[entity]['usage_frequency']
        recency_bonus = 0.1 if self._is_recently_accessed(entity) else 0
        
        self.critical_knowledge[entity]['importance_score'] = min(1.0, 
            0.5 + (frequency * 0.1) + recency_bonus)
    
    def _is_recently_accessed(self, entity: str) -> bool:
        """Check if knowledge entity was accessed recently."""
        if entity not in self.critical_knowledge:
            return False
        
        last_accessed = datetime.fromisoformat(
            self.critical_knowledge[entity]['last_accessed']
        )
        return datetime.now() - last_accessed < timedelta(hours=24)
    
    def get_policy_evolution_summary(self) -> Dict:
        """Get a summary of policy evolution over time."""
        if not self.policy_timeline:
            return {'status': 'no_policies_recorded'}
        
        performances = [p['performance'] for p in self.policy_timeline]
        
        return {
            'total_policies': len(self.policy_timeline),
            'performance_trend': {
                'initial': performances[0] if performances else 0,
                'current': performances[-1] if performances else 0,
                'peak': max(performances) if performances else 0,
                'average': sum(performances) / len(performances) if performances else 0
            },
            'learning_trajectory': 'improving' if len(performances) >= 2 and performances[-1] > performances[0] else 'stable_or_declining',
            'consolidation_events': len([p for p in self.policy_timeline if 'consolidation' in p.get('metadata', {})])
        }
    
    def get_knowledge_evolution_summary(self) -> Dict:
        """Get a summary of knowledge base evolution over time."""
        if not self.knowledge_timeline:
            return {'status': 'no_knowledge_changes_recorded'}
        
        change_types = {}
        for change in self.knowledge_timeline:
            change_type = change['change_type']
            change_types[change_type] = change_types.get(change_type, 0) + 1
        
        return {
            'total_changes': len(self.knowledge_timeline),
            'change_breakdown': change_types,
            'critical_knowledge_count': len(self.critical_knowledge),
            'recent_activity': len([c for c in self.knowledge_timeline 
                                  if self._is_recent_timestamp(c['timestamp'])])
        }
    
    def _is_recent_timestamp(self, timestamp_str: str) -> bool:
        """Check if a timestamp is recent (within last 24 hours)."""
        timestamp = datetime.fromisoformat(timestamp_str)
        return datetime.now() - timestamp < timedelta(hours=24)
    
    def export_timeline(self) -> Dict:
        """Export the complete temporal timeline for analysis."""
        return {
            'policy_timeline': self.policy_timeline,
            'knowledge_timeline': self.knowledge_timeline,
            'performance_timeline': self.performance_timeline,
            'temporal_constraints': self.temporal_constraints,
            'critical_knowledge': self.critical_knowledge
        }
