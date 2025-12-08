"""
Logic Engine for Child AI
This module implements the core mathematical logic processing capabilities, including
first-order predicate logic, non-monotonic logic, and temporal logic.
"""

from typing import Dict, List, Set, Tuple, Union, Optional, Any
from dataclasses import dataclass, field

# --- Core Data Structures ---

@dataclass(frozen=True, eq=True)
class Variable:
    name: str
    def __repr__(self): return f"Var({self.name})"

@dataclass(frozen=True, eq=True)
class Constant:
    name: str
    def __repr__(self): return f"Const({self.name})"

Term = Union[Variable, Constant]

@dataclass(frozen=True, eq=True)
class Predicate:
    name: str
    terms: Tuple[Term, ...] = field(default_factory=tuple)
    def __repr__(self):
        return f"{self.name}({', '.join(map(repr, self.terms))})" if self.terms else self.name
    def substitute(self, substitution: 'Substitution') -> 'Predicate':
        new_terms = tuple(substitution.get(term, term) for term in self.terms)
        return Predicate(self.name, new_terms)

Substitution = Dict[Variable, Term]

@dataclass(frozen=True, eq=True)
class Rule:
    premise: Predicate
    conclusion: Predicate
    def __repr__(self): return f"{self.premise} -> {self.conclusion}"

@dataclass(frozen=True, eq=True)
class DefaultRule:
    premise: Predicate
    conclusion: Predicate
    def __repr__(self): return f"{self.premise} ~> {self.conclusion}"

@dataclass(frozen=True, eq=True)
class TemporalRule:
    """Represents a temporal rule, e.g., Before(event1, event2)."""
    operator: str  # e.g., 'Before', 'After'
    events: Tuple[Predicate, Predicate]
    def __repr__(self): return f"{self.operator}({self.events[0]}, {self.events[1]})"

# --- Unification ---

def unify(x: Any, y: Any, subst: Substitution) -> Optional[Substitution]:
    if subst is None: return None
    if x == y: return subst
    if isinstance(x, Variable): return unify_variable(x, y, subst)
    if isinstance(y, Variable): return unify_variable(y, x, subst)
    if isinstance(x, Predicate) and isinstance(y, Predicate):
        if x.name != y.name or len(x.terms) != len(y.terms): return None
        for t1, t2 in zip(x.terms, y.terms):
            subst = unify(t1, t2, subst)
            if subst is None: return None
        return subst
    return None

def unify_variable(var: Variable, x: Term, subst: Substitution) -> Optional[Substitution]:
    if var in subst: return unify(subst[var], x, subst)
    new_subst = subst.copy()
    new_subst[var] = x
    return new_subst

# --- Knowledge Base ---

class KnowledgeBase:
    def __init__(self):
        self.facts: Set[Predicate] = set()
        self.rules: List[Rule] = []
        self.default_rules: List[DefaultRule] = []
        self.temporal_facts: List[Predicate] = [] # For HappensAt(event, time)

    def add_fact(self, fact: Predicate):
        if fact.name == "HappensAt": self.temporal_facts.append(fact)
        else: self.facts.add(fact)

    def add_rule(self, rule: Rule): self.rules.append(rule)
    def add_default_rule(self, rule: DefaultRule): self.default_rules.append(rule)

# --- Inference Engine ---

class InferenceEngine:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.derived_facts: Set[Predicate] = set()

    def query(self, goal: Predicate) -> bool:
        if self._backward_chaining_ask(goal, {}): return True
        return self._nml_ask(goal, {})

    def temporal_query(self, query: TemporalRule) -> bool:
        """Handles temporal queries like Before(event1, event2)."""
        event1_time = self._find_event_time(query.events[0])
        event2_time = self._find_event_time(query.events[1])

        if event1_time is None or event2_time is None: return False

        if query.operator == "Before": return event1_time < event2_time
        if query.operator == "After": return event1_time > event2_time
        return False

    def _find_event_time(self, event: Predicate) -> Optional[int]:
        """Finds the timestamp for a given event."""
        for tf in self.kb.temporal_facts:
            if tf.name == "HappensAt" and unify(tf.terms[0], event, {}) is not None:
                time_const = tf.terms[1]
                if isinstance(time_const, Constant):
                    return int(time_const.name)
        return None

    def _backward_chaining_ask(self, query: Predicate, subst: Substitution) -> bool:
        # Standard backward chaining logic...
        for fact in self.kb.facts:
            if unify(fact, query, subst.copy()) is not None: return True
        for rule in self.kb.rules:
            rule = self._standardize_variables(rule)
            unified_subst = unify(rule.conclusion, query, subst.copy())
            if unified_subst and self._backward_chaining_ask(rule.premise.substitute(unified_subst), unified_subst):
                self.derived_facts.add(query)
                return True
        return False

    def _nml_ask(self, query: Predicate, subst: Substitution) -> bool:
        # NML backward chaining logic...
        for d_rule in self.kb.default_rules:
            rule = self._standardize_variables(d_rule)
            unified_subst = unify(rule.conclusion, query, subst.copy())
            if unified_subst and self._backward_chaining_ask(rule.premise.substitute(unified_subst), unified_subst):
                negated_conclusion = Predicate(f"Not{rule.conclusion.name}", rule.conclusion.terms)
                if not self._backward_chaining_ask(negated_conclusion.substitute(unified_subst), {}):
                    self.derived_facts.add(query)
                    return True
        return False

    _var_counter = 0
    def _standardize_variables(self, rule: Union[Rule, DefaultRule]) -> Any:
        # Variable standardization logic...
        self._var_counter += 1
        subst = {}
        def get_vars(p): return [t for t in p.terms if isinstance(t, Variable)]
        all_vars = set(get_vars(rule.premise) + get_vars(rule.conclusion))
        for var in all_vars:
            subst[var] = Variable(f"{var.name}_{self._var_counter}")

        new_premise = rule.premise.substitute(subst)
        new_conclusion = rule.conclusion.substitute(subst)

        if isinstance(rule, DefaultRule): return DefaultRule(new_premise, new_conclusion)
        return Rule(new_premise, new_conclusion)

# --- Main Logic Engine ---

class LogicEngine:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.inference_engine = InferenceEngine(self.knowledge_base)

    def add_fact(self, fact: Predicate): self.knowledge_base.add_fact(fact)
    def add_rule(self, rule: Rule): self.knowledge_base.add_rule(rule)
    def add_default_rule(self, rule: DefaultRule): self.knowledge_base.add_default_rule(rule)

    def query(self, query: Union[Predicate, TemporalRule]) -> bool:
        if isinstance(query, TemporalRule):
            return self.inference_engine.temporal_query(query)
        return self.inference_engine.query(query)

    def get_all_facts(self) -> Set[Predicate]: return self.knowledge_base.facts

    def get_statistics(self) -> Dict[str, int]:
        return {
            "total_facts": len(self.knowledge_base.facts),
            "temporal_facts": len(self.knowledge_base.temporal_facts),
            "total_rules": len(self.knowledge_base.rules),
            "total_default_rules": len(self.knowledge_base.default_rules),
            "derived_facts": len(self.inference_engine.derived_facts)
        }

# --- Example Usage ---
if __name__ == "__main__":
    engine = LogicEngine()

    # Add temporal facts
    engine.add_fact(Predicate("HappensAt", (Predicate("Login", (Constant("UserA"),)), Constant("100"))))
    engine.add_fact(Predicate("HappensAt", (Predicate("Logout", (Constant("UserA"),)), Constant("200"))))

    # Temporal query
    query = TemporalRule("Before", (
        Predicate("Login", (Constant("UserA"),)),
        Predicate("Logout", (Constant("UserA"),))
    ))

    result = engine.query(query)
    print(f"Temporal Query: {query} -> Result: {result}") # Expected: True

    print("\n--- Statistics ---")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"- {key}: {value}")
