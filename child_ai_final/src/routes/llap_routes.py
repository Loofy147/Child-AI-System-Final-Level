from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)
llap_bp = Blueprint('llap', __name__)

@llap_bp.route('/run_episode', methods=['POST'])
def run_episode():
    """API endpoint to trigger a single LLAP learning episode."""
    data = request.get_json()
    scenario_id = data.get('scenario_id', 'default_scenario')
    scenario_data = data.get('scenario_data', {})
    
    try:
        llap_system = current_app.llap_system
        result = llap_system.run_learning_episode(scenario_id, scenario_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in LLAP run episode route: {e}")
        return jsonify({'error': str(e)}), 500

@llap_bp.route('/status', methods=['GET'])
def get_status():
    """API endpoint to get comprehensive LLAP system status."""
    try:
        llap_system = current_app.llap_system
        status = llap_system.get_lifelong_learning_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting LLAP status: {e}")
        return jsonify({'error': str(e)}), 500

@llap_bp.route('/timeline', methods=['GET'])
def get_timeline():
    """API endpoint to get the complete learning timeline."""
    try:
        llap_system = current_app.llap_system
        timeline = llap_system.export_learning_timeline()
        return jsonify(timeline)
    except Exception as e:
        logger.error(f"Error getting LLAP timeline: {e}")
        return jsonify({'error': str(e)}), 500

@llap_bp.route('/policy_history', methods=['GET'])
def get_policy_history():
    """API endpoint to get the history of policy updates."""
    try:
        llap_system = current_app.llap_system
        timeline = llap_system.export_learning_timeline()
        policy_timeline = timeline.get('policy_timeline', [])
        return jsonify({'history': policy_timeline, 'count': len(policy_timeline)})
    except Exception as e:
        logger.error(f"Error getting LLAP policy history: {e}")
        return jsonify({'error': str(e)}), 500

@llap_bp.route('/trigger_consolidation', methods=['POST'])
def trigger_consolidation():
    """API endpoint to manually trigger knowledge consolidation."""
    try:
        llap_system = current_app.llap_system
        result = llap_system._trigger_knowledge_consolidation()
        return jsonify({
            'status': 'consolidation_triggered',
            'result': result
        })
    except Exception as e:
        logger.error(f"Error triggering consolidation: {e}")
        return jsonify({'error': str(e)}), 500

@llap_bp.route('/adjust_strategy', methods=['POST'])
def adjust_strategy():
    """API endpoint to manually adjust learning strategy."""
    data = request.get_json()
    strategy = data.get('strategy')
    
    if strategy not in ['conservative', 'aggressive', 'balanced']:
        return jsonify({'error': 'Invalid strategy. Must be one of: conservative, aggressive, balanced'}), 400
    
    try:
        llap_system = current_app.llap_system
        
        # Apply strategy parameters
        strategy_params = llap_system.adaptation_strategies[strategy]
        llap_system.learning_rate = strategy_params['learning_rate']
        llap_system.knowledge_retention_rate = strategy_params['retention']
        llap_system.current_strategy = strategy
        
        return jsonify({
            'status': 'strategy_updated',
            'new_strategy': strategy,
            'parameters': strategy_params
        })
    except Exception as e:
        logger.error(f"Error adjusting strategy: {e}")
        return jsonify({'error': str(e)}), 500
