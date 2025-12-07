from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)
akd_bp = Blueprint('akd', __name__)

@akd_bp.route('/discover/web', methods=['POST'])
def discover_web():
    """API endpoint to trigger web-based knowledge discovery."""
    data = request.get_json()
    url = data.get('url')
    query = data.get('query')
    
    if not url or not query:
        return jsonify({'error': 'Missing required fields: url and query'}), 400
    
    try:
        akd_system = current_app.akd_system
        result = akd_system.discover_from_web(url, query)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in web discovery route: {e}")
        return jsonify({'error': str(e)}), 500

@akd_bp.route('/discover/api', methods=['POST'])
def discover_api():
    """API endpoint to trigger API-based knowledge discovery."""
    data = request.get_json()
    api_endpoint = data.get('api_endpoint')
    params = data.get('params', {})
    
    if not api_endpoint:
        return jsonify({'error': 'Missing required field: api_endpoint'}), 400
    
    try:
        akd_system = current_app.akd_system
        result = akd_system.discover_from_api(api_endpoint, params)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in API discovery route: {e}")
        return jsonify({'error': str(e)}), 500

@akd_bp.route('/history', methods=['GET'])
def get_history():
    """API endpoint to get the history of AKD attempts."""
    try:
        akd_system = current_app.akd_system
        history = akd_system.get_akd_history()
        return jsonify({'history': history, 'count': len(history)})
    except Exception as e:
        logger.error(f"Error getting AKD history: {e}")
        return jsonify({'error': str(e)}), 500
