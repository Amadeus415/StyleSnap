from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Load config
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.update(test_config)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import blueprints
    from .routes import main
    app.register_blueprint(main)
    
    # Push an application context
    ctx = app.app_context()
    ctx.push()
    
    # Import models and create tables
    with app.app_context():
        from . import models
        db.create_all()
    
    return app