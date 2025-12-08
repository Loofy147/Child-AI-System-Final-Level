"""This module contains custom command-line interface (CLI) commands for the application."""
import click
from flask.cli import with_appcontext
from .child_ai.extensions import learning_module

@click.command(name='seed_db')
@with_appcontext
def seed_db():
    """Seeds the database with a set of initial learning examples.

    This command populates the knowledge base with some fundamental facts
    to ensure the AI has a baseline of knowledge when it starts.
    """
    learning_module.learn_from_feedback("Socrates is a human", "Human(Socrates)", True)
    learning_module.learn_from_feedback("Socrates is mortal", "Mortal(Socrates)", True)
    learning_module.learn_from_feedback("Plato is a human", "Human(Plato)", True)
    click.echo('Database seeded successfully.')

def create_cli(app):
    """Register CLI commands with the Flask app.

    Args:
        app: The Flask application instance.
    """
    app.cli.add_command(seed_db)
