import os

# Get the absolute path of the instance folder
instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f"sqlite:///{os.path.join(instance_path, 'app_dev.db')}"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(instance_path, 'app.db')}"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
