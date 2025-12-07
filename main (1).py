#!/usr/bin/env python3
"""
Child AI Final System - Main Application
A Neuro-Symbolic Continual Learning Agent with Advanced Mathematical Logics

This is the main entry point for the Child AI Final system, implementing:
- Automated Knowledge Discovery (AKD)
- Self-Correction and Integrity System (SCIS)
- Lifelong Learning and Adaptive Policy (LLAP)
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from core.logic_engine import LogicEngine
from core.knowledge_base import KnowledgeBase
from modules.akd_system import AKDSystem
from modules.scis_system import SCISSystem
from modules.llap_system import LLAPSystem
from routes.akd_routes import akd_bp
from routes.scis_routes import scis_bp
from routes.llap_routes import llap_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins="*")
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialize core components
    logger.info("Initializing Child AI Final System...")
    
    # Initialize Knowledge Base
    knowledge_base = KnowledgeBase()
    app.knowledge_base = knowledge_base
    
    # Initialize Logic Engine
    logic_engine = LogicEngine(knowledge_base)
    app.logic_engine = logic_engine
    
    # Initialize AKD System
    akd_system = AKDSystem(knowledge_base, logic_engine)
    app.akd_system = akd_system
    
    # Initialize SCIS System
    scis_system = SCISSystem(knowledge_base, logic_engine)
    app.scis_system = scis_system
    
    # Initialize LLAP System
    llap_system = LLAPSystem(knowledge_base, logic_engine)
    app.llap_system = llap_system
    
    # Register blueprints
    app.register_blueprint(akd_bp, url_prefix='/api/akd')
    app.register_blueprint(scis_bp, url_prefix='/api/scis')
    app.register_blueprint(llap_bp, url_prefix='/api/llap')
    
    # Main routes
    @app.route('/')
    def index():
        """Main dashboard for the Child AI Final system."""
        return render_template('dashboard.html')
    
    @app.route('/api/status')
    def status():
        """Get system status and metrics."""
        try:
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'system': 'Child AI Final System',
                'version': '1.0.0',
                'status': 'operational',
                'components': {
                    'knowledge_base': {
                        'facts_count': len(knowledge_base.facts),
                        'rules_count': len(knowledge_base.rules),
                        'status': 'active'
                    },
                    'logic_engine': {
                        'status': 'active',
                        'last_inference': logic_engine.last_inference_time if hasattr(logic_engine, 'last_inference_time') else None
                    },
                    'akd_system': {
                        'status': 'active',
                        'discoveries_count': akd_system.get_discoveries_count()
                    },
                    'scis_system': {
                        'status': 'active',
                        'corrections_count': scis_system.get_corrections_count()
                    },
                    'llap_system': {
                        'status': 'active',
                        'learning_episodes': llap_system.get_learning_episodes_count()
                    }
                }
            }
            return jsonify(status_data)
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/query', methods=['POST'])
    def query():
        """Process a logical query through the system."""
        try:
            data = request.get_json()
            query_text = data.get('query', '')
            
            if not query_text:
                return jsonify({'error': 'Query text is required'}), 400
            
            # Process the query through the logic engine
            result = logic_engine.process_query(query_text)
            
            return jsonify({
                'query': query_text,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info("Child AI Final System initialized successfully!")
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get host and port from environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Child AI Final System on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
