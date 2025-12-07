"""
Logic Engine for Child AI
This module implements the core mathematical logic processing capabilities,
including first-order predicate logic, unification, and inference mechanisms
with support for Non-Monotonic Logic (NML) through default rules.
"""

from typing import Dict, List, Set, Tuple, Union, Optional, Any
from dataclasses import dataclass, field

# --- Core Data Structures for First-Order Logic ---

@dataclass(frozen=True, eq=True)
class Variable:
    """Represents a variable in a logical expression (e.g., x, y)."""
    name: str
    def __repr__(self):
        return f"Var({self.name})"

@dataclass(frozen=True, eq=True)
class Constant:
    """Represents a constant in a logical expression (e.g., Socrates, Plato)."""
    name: str
    def __repr__(self):
        return f"Const({self.name})"

Term = Union[Variable, Constant]

@dataclass(frozen=True, eq=True)
class Predicate:
    """Represents a predicate with a name and a list of terms."""
    name: str
    terms: Tuple[Term, ...] = field(default_factory=tuple)

    def __repr__(self):
        if not self.terms:
            return self.name
        return f"{self.name}({', '.join(map(repr, self.terms))})"

    def substitute(self, substitution: 'Substitution') -> 'Predicate':
        """Substitute variables in the predicate's terms."""
        new_terms = tuple(substitution.get(term, term) for term in self.terms)
        return Predicate(self.name, new_terms)

# A substitution is a mapping from Variables to Terms
Substitution = Dict[Variable, Term]

@dataclass(frozen=True, eq=True)
class Rule:
    """Represents a standard logical rule (premise -> conclusion)."""
    premise: Predicate
    conclusion: Predicate

    def __repr__(self):
        return f"{self.premise} -> {self.conclusion}"

@dataclass(frozen=True, eq=True)
class DefaultRule:
    """Represents a default rule for non-monotonic reasoning."""
    premise: Predicate
    conclusion: Predicate

    def __repr__(self):
        return f"{self.premise} ~> {self.conclusion}"

# --- Unification ---

def unify(x: Any, y: Any, subst: Substitution) -> Optional[Substitution]:
    """Unify two logical expressions x and y with a given substitution."""
    if subst is None: return None
    if x == y: return subst
    if isinstance(x, Variable): return unify_variable(x, y, subst)
    if isinstance(y, Variable): return unify_variable(y, x, subst)
    if isinstance(x, Predicate) and isinstance(y, Predicate):
        if x.name != y.name or len(x.terms) != len(y.terms):
            return None
        for t1, t2 in zip(x.terms, y.terms):
            subst = unify(t1, t2, subst)
            if subst is None: return None
        return subst
    return None

def unify_variable(var: Variable, x: Term, subst: Substitution) -> Optional[Substitution]:
    """Unify a variable with a term."""
    if var in subst:
        return unify(subst[var], x, subst)
    new_subst = subst.copy()
    new_subst[var] = x
    return new_subst

# --- Knowledge Base ---

class KnowledgeBase:
    """Stores and manages logical facts, standard rules, and default rules."""

    def __init__(self):
        self.facts: Set[Predicate] = set()
        self.rules: List[Rule] = []
        self.default_rules: List[DefaultRule] = []

    def add_fact(self, fact: Predicate): self.facts.add(fact)
    def add_rule(self, rule: Rule): self.rules.append(rule)
    def add_default_rule(self, rule: DefaultRule): self.default_rules.append(rule)
    def get_facts(self) -> Set[Predicate]: return self.facts.copy()
    def get_rules(self) -> List[Rule]: return self.rules.copy()
    def get_default_rules(self) -> List[DefaultRule]: return self.default_rules.copy()

# --- Inference Engine ---

class InferenceEngine:
    """Implements logical inference mechanisms, including default reasoning."""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.derived_facts: Set[Predicate] = set()

    def query(self, goal: Predicate) -> bool:
        """Main query method that incorporates non-monotonic reasoning."""
        # 1. First, try to prove the goal using standard logic.
        if self._backward_chaining_ask(goal, {}):
            return True

        # 2. If that fails, try to prove it using default rules.
        return self._nml_ask(goal, {})

    def _backward_chaining_ask(self, query: Predicate, subst: Substitution) -> bool:
        """Standard backward chaining for monotonic reasoning."""
        for fact in self.kb.get_facts():
            unified_subst = unify(fact, query, subst.copy())
            if unified_subst is not None: return True

        for rule in self.kb.get_rules():
            rule = self._standardize_variables(rule)
            unified_subst = unify(rule.conclusion, query, subst.copy())
            if unified_subst is not None:
                if self._backward_chaining_ask(rule.premise.substitute(unified_subst), unified_subst):
                    self.derived_facts.add(query)
                    return True
        return False

    def _nml_ask(self, query: Predicate, subst: Substitution) -> bool:
        """Backward chaining with default rules (Non-Monotonic Logic)."""
        for d_rule in self.kb.get_default_rules():
            rule = self._standardize_variables(d_rule)
            unified_subst = unify(rule.conclusion, query, subst.copy())
            if unified_subst is not None:
                # Prove the premise using standard logic
                if self._backward_chaining_ask(rule.premise.substitute(unified_subst), unified_subst):
                    # Check for contradictions
                    negated_conclusion = Predicate(f"Not{rule.conclusion.name}", rule.conclusion.terms)
                    negated_conclusion_subst = negated_conclusion.substitute(unified_subst)

                    if not self._backward_chaining_ask(negated_conclusion_subst, {}):
                        self.derived_facts.add(query)
                        return True
        return False

    _var_counter = 0
    def _standardize_variables(self, rule: Union[Rule, DefaultRule]) -> Union[Rule, DefaultRule]:
        """Rename variables in a rule to be unique."""
        self._var_counter += 1
        subst = {}

        def get_vars(predicate):
            return [t for t in predicate.terms if isinstance(t, Variable)]

        all_vars = set(get_vars(rule.premise) + get_vars(rule.conclusion))

        for var in all_vars:
            subst[var] = Variable(f"{var.name}_{self._var_counter}")

        new_premise = rule.premise.substitute(subst)
        new_conclusion = rule.conclusion.substitute(subst)

        if isinstance(rule, DefaultRule):
            return DefaultRule(new_premise, new_conclusion)
        return Rule(new_premise, new_conclusion)

# --- Main Logic Engine ---

class LogicEngine:
    """Main logic engine that coordinates all logical operations."""

    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.inference_engine = InferenceEngine(self.knowledge_base)

    def add_fact(self, fact: Predicate): self.knowledge_base.add_fact(fact)
    def add_rule(self, rule: Rule): self.knowledge_base.add_rule(rule)
    def add_default_rule(self, rule: DefaultRule): self.knowledge_base.add_default_rule(rule)

    def query(self, query: Predicate) -> bool:
        """Query the knowledge base using both standard and default reasoning."""
        return self.inference_engine.query(query)

    def get_all_facts(self) -> Set[Predicate]:
        return self.knowledge_base.get_facts()

    def get_statistics(self) -> Dict[str, int]:
        return {
            "total_facts": len(self.knowledge_base.get_facts()),
            "total_rules": len(self.knowledge_base.get_rules()),
            "total_default_rules": len(self.knowledge_base.get_default_rules()),
            "derived_facts": len(self.inference_engine.derived_facts)
        }

# --- Example Usage ---
if __name__ == "__main__":
    engine = LogicEngine()
    x = Variable("x")

    # --- Knowledge ---
    # Facts
    engine.add_fact(Predicate("Bird", (Constant("Tweety"),)))
    engine.add_fact(Predicate("Penguin", (Constant("Tux"),)))

    # Standard rule: All penguins are birds.
    engine.add_rule(Rule(
        premise=Predicate("Penguin", (x,)),
        conclusion=Predicate("Bird", (x,))
    ))

    # Fact: Penguins cannot fly (negation of the default).
    engine.add_fact(Predicate("NotFlies", (Constant("Tux"),)))

    # Default rule: Birds typically fly.
    engine.add_default_rule(DefaultRule(
        premise=Predicate("Bird", (x,)),
        conclusion=Predicate("Flies", (x,))
    ))

    # --- Queries ---
    print("--- Non-Monotonic Logic Queries ---")

    query1 = Predicate("Flies", (Constant("Tweety"),))
    result1 = engine.query(query1)
    print(f"Query: Can Tweety fly? ({query1}) -> Result: {result1}") # Expected: True

    query2 = Predicate("Flies", (Constant("Tux"),))
    result2 = engine.query(query2)
    print(f"Query: Can Tux fly? ({query2}) -> Result: {result2}") # Expected: False

    query3 = Predicate("Bird", (Constant("Tux"),))
    result3 = engine.query(query3)
    print(f"Query: Is Tux a bird? ({query3}) -> Result: {result3}") # Expected: True

    print("\n--- Statistics ---")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"- {key}: {value}")
