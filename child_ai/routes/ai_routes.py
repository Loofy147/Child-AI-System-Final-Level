"""
API Routes for Child AI System
This module defines the REST API endpoints for interacting with the Child AI.
"""

from flask import Blueprint, request, jsonify
from ..logic_engine import Predicate, Constant, Variable, Rule
from ..extensions import logic_engine, knowledge_integrator
import re

ai_bp = Blueprint('ai', __name__)

# --- Helper function to parse predicate strings ---
def parse_predicate(p_str: str) -> Predicate:
    """Parses a string like 'Mortal(Socrates)' into a Predicate object."""
    match = re.match(r"(\w+)\((.*)\)", p_str)
    if not match:
        return Predicate(p_str) # A predicate with no arguments

    name = match.group(1)
    args_str = match.group(2)

    terms = []
    if args_str:
        for term_str in args_str.split(','):
            term_str = term_str.strip()
            if term_str[0].islower(): # Convention: variables start with lowercase
                terms.append(Variable(term_str))
            else:
                terms.append(Constant(term_str))

    return Predicate(name, tuple(terms))


# --- API Routes ---

@ai_bp.route('/status', methods=['GET'])
def get_status():
    """Get the current status of the AI system."""
    stats = logic_engine.get_statistics()
    return jsonify({
        'status': 'active',
        'logic_engine': stats,
        'message': 'Child AI is running successfully'
    })

@ai_bp.route('/facts', methods=['GET'])
def get_facts():
    """Get all facts from the knowledge base."""
    facts = [str(f) for f in logic_engine.get_all_facts()]
    return jsonify({'facts': sorted(facts), 'count': len(facts)})

@ai_bp.route('/facts', methods=['POST'])
def add_fact():
    """Add a new fact to the knowledge base."""
    data = request.get_json()
    if not data or 'fact' not in data:
        return jsonify({'error': "Missing 'fact' in request body."}), 400

    try:
        fact = parse_predicate(data['fact'])
        logic_engine.add_fact(fact)
        return jsonify({'message': f"Fact '{fact}' added successfully."}), 201
    except Exception as e:
        return jsonify({'error': f"Failed to parse or add fact: {e}"}), 400

@ai_bp.route('/rules', methods=['POST'])
def add_rule():
    """Add a new rule to the knowledge base."""
    data = request.get_json()
    if not data or 'premise' not in data or 'conclusion' not in data:
        return jsonify({'error': "Missing 'premise' or 'conclusion' in request body."}), 400

    try:
        premise = parse_predicate(data['premise'])
        conclusion = parse_predicate(data['conclusion'])
        rule = Rule(premise, conclusion)
        logic_engine.add_rule(rule)
        return jsonify({'message': f"Rule '{rule}' added successfully."}), 201
    except Exception as e:
        return jsonify({'error': f"Failed to parse or add rule: {e}"}), 400

@ai_bp.route('/query', methods=['POST'])
def query_knowledge():
    """Query the knowledge base using backward chaining."""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': "Missing 'query' in request body."}), 400

    try:
        query = parse_predicate(data['query'])
        result = logic_engine.query(query)
        return jsonify({'query': str(query), 'result': result})
    except Exception as e:
        return jsonify({'error': f"Failed to parse or execute query: {e}"}), 400

@ai_bp.route('/infer', methods=['POST'])
def infer_all_facts():
    """Run forward chaining to infer all possible facts."""
    logic_engine.infer_all()
    new_facts = [str(f) for f in logic_engine.derived_facts]
    return jsonify({
        'message': 'Inference complete.',
        'newly_derived_facts': sorted(new_facts),
        'total_facts': len(logic_engine.get_all_facts())
    })

# Initialize with some default knowledge for demonstration
def add_initial_knowledge():
    socrates = Constant("Socrates")
    plato = Constant("Plato")
    x = Variable("x")

    logic_engine.add_fact(Predicate("Human", (socrates,)))
    logic_engine.add_fact(Predicate("Human", (plato,)))

    logic_engine.add_rule(Rule(
        premise=Predicate("Human", (x,)),
        conclusion=Predicate("Mortal", (x,))
    ))

add_initial_knowledge()
