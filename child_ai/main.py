"""This module contains the main application factory for the Child AI system."""
import os
from flask import Flask, send_from_directory
from config import config
from .models.user import db
from .routes.user import user_bp
from .routes.ai_routes import ai_bp
from .routes.learning_routes import learning_bp

def create_app(config_name):
    """Create and configure an instance of the Flask application.

    Args:
        config_name: The name of the configuration to use for the application.

    Returns:
        A Flask application instance.
    """
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config.from_object(config[config_name])

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Serve static files.

        Args:
            path: The path to the static file to serve.

        Returns:
            A Flask response with the static file, or a 404 error if the file is not found.
        """
        static_folder_path = app.static_folder
        if static_folder_path is None:
                return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404

    return app
