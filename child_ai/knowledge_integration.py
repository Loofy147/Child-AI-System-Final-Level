"""
Knowledge Integration Module for Child AI
This module handles the integration of knowledge from various sources using
spaCy for advanced text processing and a more robust conflict resolution system.
"""

import spacy
from typing import Dict, List, Any, Optional, Tuple
from .logic_engine import Predicate, Constant, Rule

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class TextKnowledgeExtractor:
    """Extracts knowledge from text using NLP techniques."""

    def extract(self, text: str) -> List[Predicate]:
        """Extracts predicates from text using NER and dependency parsing."""
        doc = nlp(text)
        predicates = []

        for sent in doc.sents:
            # Simple pattern: (Subject, Verb, Object)
            subjects = [tok for tok in sent if "subj" in tok.dep_]
            objects = [tok for tok in sent if "obj" in tok.dep_]

            if subjects and objects:
                # Find the main verb
                verb = sent.root
                # Capitalize for predicate naming convention
                predicate_name = verb.lemma_.capitalize()

                # For simplicity, we'll take the first subject and object
                subject_const = Constant(subjects[0].text.capitalize())
                object_const = Constant(objects[0].text.capitalize())

                predicates.append(Predicate(predicate_name, (subject_const, object_const)))

        return predicates

class KnowledgeIntegrator:
    """Main class for integrating knowledge from various sources."""

    def __init__(self, logic_engine):
        self.logic_engine = logic_engine
        self.text_extractor = TextKnowledgeExtractor()
        self.integration_log: List[Dict[str, Any]] = []

    def integrate_text(self, text: str, source_name: str = "manual_input") -> int:
        """Integrate knowledge from text."""
        predicates = self.text_extractor.extract(text)

        for pred in predicates:
            self.logic_engine.add_fact(pred)
            self.integration_log.append({
                'source': source_name,
                'fact': str(pred),
                'type': 'text_extraction'
            })

        return len(predicates)

    def resolve_conflicts(self) -> List[Dict[str, Any]]:
        """
        Identify and resolve conflicts in the knowledge base.
        This is a more advanced placeholder that looks for contradictory predicates.
        """
        conflicts = []
        all_facts = self.logic_engine.get_all_facts()

        # Look for facts like `Predicate(A, B)` and `NotPredicate(A, B)`
        # (Assuming a `Not` prefix for contradictions)
        fact_map = {str(f): f for f in all_facts}

        for fact_str, fact in fact_map.items():
            negated_fact_str_v1 = f"Not{fact.name}({', '.join(map(str, fact.terms))})"
            negated_fact_str_v2 = f"¬{fact.name}({', '.join(map(str, fact.terms))})" # Common alt

            if negated_fact_str_v1 in fact_map or negated_fact_str_v2 in fact_map:
                conflicts.append({
                    'type': 'contradiction',
                    'fact1': fact_str,
                    'fact2': negated_fact_str_v1 if negated_fact_str_v1 in fact_map else negated_fact_str_v2
                    # In a real system, you'd add resolution logic here
                })

        return conflicts

# Example Usage
if __name__ == "__main__":
    from .logic_engine import LogicEngine

    engine = LogicEngine()
    integrator = KnowledgeIntegrator(engine)

    sample_text = "Socrates teaches Plato. Aristotle wrote Organon."
    print(f"Integrating from text: '{sample_text}'")

    count = integrator.integrate_text(sample_text)
    print(f"Integrated {count} facts.")

    print("\nFacts in knowledge base:")
    for fact in engine.get_all_facts():
        print(f"- {fact}")

    # Example of a conflict
    engine.add_fact(Predicate("NotTeaches", (Constant("Socrates"), Constant("Plato"))))

    print("\nChecking for conflicts:")
    conflicts = integrator.resolve_conflicts()
    if conflicts:
        for conflict in conflicts:
            print(f"- Found conflict: {conflict}")
    else:
        print("- No conflicts found.")
