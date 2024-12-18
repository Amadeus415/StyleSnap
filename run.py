from app import create_app, db
import ssl
import socket

app = create_app()

# Push application context
ctx = app.app_context()
ctx.push()

if __name__ == '__main__':
    # Get local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Local IP Address: {local_ip}")
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Load certificate
    context.load_cert_chain('localhost+1.pem', 'localhost+1-key.pem')
    
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=context,
        debug=True
    )