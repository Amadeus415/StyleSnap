from flask import Flask
from app.routes import main
from config import Config
import ssl
import os

def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config.from_object(Config)
    
    # Set secret key for sessions
    app.secret_key = Config.SECRET_KEY
    
    # Register blueprints
    app.register_blueprint(main)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Set up HTTPS context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    # Run the app
    app.run(
        host='127.0.0.1',
        port=5000,
        ssl_context=context,
        debug=True
    ) 