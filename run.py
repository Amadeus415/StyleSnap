from flask import Flask
from app.routes import main
from config import Config
import ssl
import os
import socket

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
    
    # Create SSL context with verification flags
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Load certificate
    context.load_cert_chain('localhost+1.pem', 'localhost+1-key.pem')
    
    app.run(
        host='127.0.0.1',
        port=5000,
        ssl_context=context,
        debug=True
    )