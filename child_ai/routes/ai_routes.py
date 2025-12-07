"""
API Routes for Child AI System
This module defines the REST API endpoints for interacting with the Child AI.
"""

from flask import Blueprint, request, jsonify
from ..logic_engine import Predicate, Constant, Variable, Rule, DefaultRule, TemporalRule
from ..extensions import logic_engine
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
        # This is a simplified parser; a robust implementation would handle nested predicates
        # For now, we assume simple terms (Constants or Variables)
        term_parts = args_str.split(',')

        # Check for nested predicates, e.g., HappensAt(Login(UserA), 100)
        # A bit of a hacky way to handle one level of nesting for temporal facts
        nested_match = re.match(r"(\w+\(.*\)).*", args_str)
        if nested_match:
             # Re-parse the nested predicate
             nested_predicate_str = nested_match.group(1)
             terms.append(parse_predicate(nested_predicate_str))
             # Handle the second term (the time)
             remaining_str = args_str.replace(nested_predicate_str, "").strip()
             if remaining_str.startswith(','):
                 time_str = remaining_str[1:].strip()
                 terms.append(Constant(time_str))
        else:
            for term_str in term_parts:
                term_str = term_str.strip()
                if term_str[0].islower():
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

@ai_bp.route('/facts', methods=['GET', 'POST'])
def handle_facts():
    """Add a new fact or get all facts from the knowledge base."""
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'fact' not in data:
            return jsonify({'error': "Missing 'fact' in request body."}), 400

        try:
            fact = parse_predicate(data['fact'])
            logic_engine.add_fact(fact)
            return jsonify({'message': f"Fact '{fact}' added successfully."}), 201
        except Exception as e:
            return jsonify({'error': f"Failed to parse or add fact: {e}"}), 400
    else: # GET request
        facts = [str(f) for f in logic_engine.get_all_facts()]
        return jsonify({'facts': sorted(facts), 'count': len(facts)})

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

@ai_bp.route('/rules/default', methods=['POST'])
def add_default_rule():
    """Add a new default rule to the knowledge base."""
    data = request.get_json()
    if not data or 'premise' not in data or 'conclusion' not in data:
        return jsonify({'error': "Missing 'premise' or 'conclusion' in request body."}), 400

    try:
        premise = parse_predicate(data['premise'])
        conclusion = parse_predicate(data['conclusion'])
        rule = DefaultRule(premise, conclusion)
        logic_engine.add_default_rule(rule)
        return jsonify({'message': f"Default rule '{rule}' added successfully."}), 201
    except Exception as e:
        return jsonify({'error': f"Failed to parse or add default rule: {e}"}), 400

@ai_bp.route('/query', methods=['POST'])
def query_knowledge():
    """Query the knowledge base for a standard predicate."""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': "Missing 'query' in request body."}), 400

    try:
        query = parse_predicate(data['query'])
        result = logic_engine.query(query)
        return jsonify({'query': str(query), 'result': result})
    except Exception as e:
        return jsonify({'error': f"Failed to parse or execute query: {e}"}), 400

@ai_bp.route('/query/temporal', methods=['POST'])
def query_temporal_knowledge():
    """Query the knowledge base for a temporal relationship."""
    data = request.get_json()
    required_fields = ['operator', 'event1', 'event2']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': "Missing 'operator', 'event1', or 'event2' in request body."}), 400

    try:
        operator = data['operator']
        event1 = parse_predicate(data['event1'])
        event2 = parse_predicate(data['event2'])

        query = TemporalRule(operator, (event1, event2))
        result = logic_engine.query(query)

        return jsonify({'query': str(query), 'result': result})
    except Exception as e:
        return jsonify({'error': f"Failed to parse or execute temporal query: {e}"}), 400
