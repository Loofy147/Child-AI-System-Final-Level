"""
Learning API Routes for Child AI System
This module defines the REST API endpoints for the learning and adaptation features.
"""

from flask import Blueprint, request, jsonify
from ..extensions import learning_module

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback to the learning module."""
    data = request.get_json()
    if not data or 'input_text' not in data or 'output_str' not in data or 'feedback' not in data:
        return jsonify({'error': "Missing required fields: 'input_text', 'output_str', 'feedback'."}), 400

    try:
        feedback = bool(data['feedback'])
        learning_module.learn_from_feedback(
            data['input_text'],
            data['output_str'],
            feedback
        )
        return jsonify({'message': 'Feedback received and processed.'}), 200
    except Exception as e:
        return jsonify({'error': f"Failed to process feedback: {e}"}), 500

@learning_bp.route('/run-cycle', methods=['POST'])
def run_learning_cycle():
    """Trigger a learning cycle to induce new rules and evaluate performance."""
    try:
        results = learning_module.run_learning_cycle()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': f"Learning cycle failed: {e}"}), 500

@learning_bp.route('/performance', methods=['GET'])
def get_performance_report():
    """Get the latest performance report."""
    report = learning_module.evaluator.evaluate(learning_module.examples)
    return jsonify(report)
