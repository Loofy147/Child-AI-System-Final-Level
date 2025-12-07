import click
from flask.cli import with_appcontext
from .child_ai.extensions import learning_module

@click.command(name='seed_db')
@with_appcontext
def seed_db():
    """Seed the database with initial learning data."""
    learning_module.learn_from_feedback("Socrates is a human", "Human(Socrates)", True)
    learning_module.learn_from_feedback("Socrates is mortal", "Mortal(Socrates)", True)
    learning_module.learn_from_feedback("Plato is a human", "Human(Plato)", True)
    click.echo('Database seeded successfully.')

def create_cli(app):
    app.cli.add_command(seed_db)
