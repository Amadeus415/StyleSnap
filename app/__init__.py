from flask import Flask
from config import Config

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.update(test_config)
    
    # Initialize extensions
    # db.init_app(app)
    
    # Register blueprints
    from app import routes
    app.register_blueprint(routes.main)
    
    return app 