from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)
scis_bp = Blueprint('scis', __name__)

@scis_bp.route('/check', methods=['GET'])
def check_consistency():
    """API endpoint to manually trigger a consistency check."""
    try:
        scis_system = current_app.scis_system
        result = scis_system.check_for_inconsistencies()
        
        return jsonify({
            'status': 'check_complete',
            'result': result
        })
    except Exception as e:
        logger.error(f"Error in SCIS check route: {e}")
        return jsonify({'error': str(e)}), 500

@scis_bp.route('/auto_correct', methods=['POST'])
def auto_correct():
    """API endpoint to trigger automatic correction of inconsistencies."""
    try:
        scis_system = current_app.scis_system
        result = scis_system.auto_correct_inconsistencies()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in SCIS auto-correct route: {e}")
        return jsonify({'error': str(e)}), 500

@scis_bp.route('/validate_fact', methods=['POST'])
def validate_fact():
    """API endpoint to validate a new fact before adding it to the knowledge base."""
    data = request.get_json()
    fact = data.get('fact')
    certainty = data.get('certainty', 1.0)
    source = data.get('source', 'user_input')
    
    if not fact:
        return jsonify({'error': 'Missing required field: fact'}), 400
    
    try:
        scis_system = current_app.scis_system
        result = scis_system.validate_new_fact(fact, certainty, source)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in SCIS validate fact route: {e}")
        return jsonify({'error': str(e)}), 500

@scis_bp.route('/nml_status', methods=['GET'])
def get_nml_status():
    """API endpoint to get the status of the NML engine."""
    try:
        scis_system = current_app.scis_system
        status = scis_system.get_nml_status()
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting NML status: {e}")
        return jsonify({'error': str(e)}), 500

@scis_bp.route('/history', methods=['GET'])
def get_history():
    """API endpoint to get the history of SCIS corrections."""
    try:
        scis_system = current_app.scis_system
        history = scis_system.inconsistency_history
        return jsonify({'history': history, 'count': len(history)})
    except Exception as e:
        logger.error(f"Error getting SCIS history: {e}")
        return jsonify({'error': str(e)}), 500
