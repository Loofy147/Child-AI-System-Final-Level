import json
from datetime import datetime

class KnowledgeBase:
    """
    Manages the symbolic knowledge base (facts, rules, and the knowledge graph).
    This serves as the stable, long-term memory for the Child AI.
    """
    def __init__(self, initial_facts=None, initial_rules=None):
        # Facts are stored as a dictionary for quick lookup and update
        # Key: Predicate string (e.g., "Mortal(Socrates)")
        # Value: Dictionary with {'certainty': float, 'source': str, 'timestamp': str}
        self.facts = initial_facts if initial_facts is not None else {}
        
        # Rules are stored as a list of logical implications
        # Each rule is a dictionary with {'rule': str, 'certainty': float, 'source': str}
        self.rules = initial_rules if initial_rules is not None else []
        
        # Initialize with a few core facts/rules for demonstration
        self._initialize_core_knowledge()

    def _initialize_core_knowledge(self):
        """Initializes the knowledge base with foundational facts and rules."""
        now = datetime.now().isoformat()
        
        # Core Facts
        self.add_fact("Human(Socrates)", 1.0, "Core Axiom", now)
        self.add_fact("Human(Plato)", 1.0, "Core Axiom", now)
        
        # Core Rules (First-Order Logic)
        self.add_rule("FORALL X (Human(X) -> Mortal(X))", 1.0, "Core Axiom")
        
        # Non-Monotonic Default Rule (for SCIS)
        self.add_rule("FORALL X (Bird(X) -> Flies(X))", 0.9, "Default Assumption")

    def add_fact(self, predicate, certainty, source, timestamp=None):
        """Adds or updates a fact in the knowledge base."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        self.facts[predicate] = {
            'certainty': certainty,
            'source': source,
            'timestamp': timestamp
        }

    def get_fact(self, predicate):
        """Retrieves a fact and its metadata."""
        return self.facts.get(predicate)

    def add_rule(self, rule_string, certainty, source):
        """Adds a new rule to the knowledge base."""
        self.rules.append({
            'rule': rule_string,
            'certainty': certainty,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })

    def get_all_rules(self):
        """Returns all rules in the knowledge base."""
        return self.rules

    def get_all_facts(self):
        """Returns all facts in the knowledge base."""
        return self.facts

    def to_json(self):
        """Serializes the knowledge base to a JSON string."""
        return json.dumps({
            'facts': self.facts,
            'rules': self.rules
        }, indent=4)

    @classmethod
    def from_json(cls, json_string):
        """Loads the knowledge base from a JSON string."""
        data = json.loads(json_string)
        return cls(initial_facts=data['facts'], initial_rules=data['rules'])
