import os
from flask import Flask, send_from_directory
from config import config
from .models.user import db
from .routes.user import user_bp
from .routes.ai_routes import ai_bp
from .routes.learning_routes import learning_bp

def create_app(config_name):
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config.from_object(config[config_name])

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
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
