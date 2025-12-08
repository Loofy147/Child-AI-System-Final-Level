"""This module is the main entry point for the Child AI system."""
from child_ai.main import create_app
from manage import create_cli
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
create_cli(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
