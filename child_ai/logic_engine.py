"""
Logic Engine for Child AI
This module implements the core mathematical logic processing capabilities,
including first-order predicate logic, unification, and inference mechanisms.
"""

from typing import Dict, List, Set, Tuple, Union, Optional, Any
from dataclasses import dataclass, field
import itertools

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
    """Represents a logical rule (premise -> conclusion)."""
    premise: Predicate
    conclusion: Predicate

    def __repr__(self):
        return f"{self.premise} -> {self.conclusion}"

# --- Unification ---

def unify(x: Any, y: Any, subst: Substitution) -> Optional[Substitution]:
    """
    Unify two logical expressions x and y with a given substitution.
    Returns a new substitution on success, or None on failure.
    """
    if subst is None:
        return None
    if x == y:
        return subst
    if isinstance(x, Variable):
        return unify_variable(x, y, subst)
    if isinstance(y, Variable):
        return unify_variable(y, x, subst)
    if isinstance(x, Predicate) and isinstance(y, Predicate):
        if x.name != y.name or len(x.terms) != len(y.terms):
            return None
        # Unify arguments recursively
        for t1, t2 in zip(x.terms, y.terms):
            subst = unify(t1, t2, subst)
            if subst is None:
                return None
        return subst
    return None

def unify_variable(var: Variable, x: Term, subst: Substitution) -> Optional[Substitution]:
    """Unify a variable with a term."""
    if var in subst:
        return unify(subst[var], x, subst)

    # Occurs check: prevent unifying a variable with a term containing that variable
    if isinstance(x, Predicate):
        if var_in_term(var, x, subst):
            return None

    new_subst = subst.copy()
    new_subst[var] = x
    return new_subst

def var_in_term(var: Variable, term: Term, subst: Substitution) -> bool:
    """Check if a variable occurs in a term, considering substitutions."""
    if isinstance(term, Constant):
        return False
    if isinstance(term, Variable):
        if term in subst:
            return var_in_term(var, subst[term], subst)
        return var == term
    if isinstance(term, Predicate):
        return any(var_in_term(var, t, subst) for t in term.terms)
    return False

# --- Knowledge Base ---

class KnowledgeBase:
    """Stores and manages logical facts and rules."""

    def __init__(self):
        self.facts: Set[Predicate] = set()
        self.rules: List[Rule] = []

    def add_fact(self, fact: Predicate):
        self.facts.add(fact)

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def get_facts(self) -> Set[Predicate]:
        return self.facts.copy()

    def get_rules(self) -> List[Rule]:
        return self.rules.copy()

# --- Inference Engine ---

class InferenceEngine:
    """Implements logical inference mechanisms using unification."""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    def forward_chaining(self) -> Set[Predicate]:
        """Perform forward chaining to derive all possible new facts."""
        new_facts = set()
        inferred_facts = self.kb.get_facts()

        while True:
            added_new_fact = False
            for rule in self.kb.get_rules():
                # Standardize variables apart to avoid conflicts
                rule = self._standardize_variables(rule)

                for fact in inferred_facts:
                    subst = unify(rule.premise, fact, {})
                    if subst is not None:
                        new_fact = rule.conclusion.substitute(subst)
                        if new_fact not in inferred_facts and new_fact not in new_facts:
                            new_facts.add(new_fact)
                            added_new_fact = True

            if not added_new_fact:
                break

            inferred_facts.update(new_facts)

        return new_facts

    def backward_chaining(self, goal: Predicate) -> bool:
        """Perform backward chaining to prove a goal."""
        return self._backward_chaining_ask(goal, {})

    def _backward_chaining_ask(self, query: Predicate, subst: Substitution) -> bool:
        # Check if query is a known fact
        for fact in self.kb.get_facts():
            unified_subst = unify(fact, query, subst.copy())
            if unified_subst is not None:
                return True

        # Check if query can be derived from rules
        for rule in self.kb.get_rules():
            rule = self._standardize_variables(rule)

            # Unify conclusion with the query
            unified_subst = unify(rule.conclusion, query, subst.copy())
            if unified_subst is not None:
                # Try to prove the premise
                if self._backward_chaining_ask(rule.premise.substitute(unified_subst), unified_subst):
                    return True

        return False

    _var_counter = 0
    def _standardize_variables(self, rule: Rule) -> Rule:
        """Rename variables in a rule to be unique."""
        self._var_counter += 1
        subst = {}

        def get_vars(predicate):
            return [t for t in predicate.terms if isinstance(t, Variable)]

        all_vars = get_vars(rule.premise) + get_vars(rule.conclusion)

        for var in set(all_vars):
            subst[var] = Variable(f"{var.name}_{self._var_counter}")

        return Rule(rule.premise.substitute(subst), rule.conclusion.substitute(subst))

# --- Main Logic Engine ---

class LogicEngine:
    """Main logic engine that coordinates all logical operations."""

    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.inference_engine = InferenceEngine(self.knowledge_base)
        self.derived_facts: Set[Predicate] = set()

    def add_fact(self, fact: Predicate):
        self.knowledge_base.add_fact(fact)

    def add_rule(self, rule: Rule):
        self.knowledge_base.add_rule(rule)

    def infer_all(self):
        """Run forward chaining to infer all possible facts."""
        newly_derived = self.inference_engine.forward_chaining()
        self.derived_facts.update(newly_derived)
        # Also add them to the main KB so they can be used for further inference
        for fact in newly_derived:
            self.knowledge_base.add_fact(fact)

    def query(self, query: Predicate) -> bool:
        """Query the knowledge base using backward chaining."""
        return self.inference_engine.backward_chaining(query)

    def get_all_facts(self) -> Set[Predicate]:
        return self.knowledge_base.get_facts() | self.derived_facts

    def get_statistics(self) -> Dict[str, int]:
        return {
            "total_facts": len(self.knowledge_base.get_facts()),
            "derived_facts": len(self.derived_facts),
            "total_rules": len(self.knowledge_base.get_rules())
        }

# --- Example Usage ---
if __name__ == "__main__":
    engine = LogicEngine()

    # Define constants and variables
    socrates = Constant("Socrates")
    plato = Constant("Plato")
    x = Variable("x")

    # Add facts
    engine.add_fact(Predicate("Human", (socrates,)))
    engine.add_fact(Predicate("Human", (plato,)))

    # Add a rule: ∀x (Human(x) -> Mortal(x))
    engine.add_rule(Rule(
        premise=Predicate("Human", (x,)),
        conclusion=Predicate("Mortal", (x,))
    ))

    print("--- Running Forward Chaining ---")
    engine.infer_all()

    print("\nAll facts in KB after inference:")
    for fact in sorted(list(engine.get_all_facts()), key=str):
        print(f"- {fact}")

    print("\n--- Running Backward Chaining Queries ---")

    query1 = Predicate("Mortal", (socrates,))
    result1 = engine.query(query1)
    print(f"Query: Is Socrates mortal? ({query1}) -> Result: {result1}")

    query2 = Predicate("Mortal", (plato,))
    result2 = engine.query(query2)
    print(f"Query: Is Plato mortal? ({query2}) -> Result: {result2}")

    query3 = Predicate("Human", (Constant("Aristotle"),))
    result3 = engine.query(query3)
    print(f"Query: Is Aristotle human? ({query3}) -> Result: {result3}")

    print("\n--- Statistics ---")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"- {key}: {value}")
