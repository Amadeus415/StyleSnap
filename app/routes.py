from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from config import Config
from functools import wraps
import uuid # for unique filename
from sqlalchemy.sql import func
#db
from . import db
from .models import User, UserPhoto, FacialAnalysis

#My utils
from .utils import get_or_create_user, save_photo, save_base64_photo, save_and_analyze_photo, cleanup_old_photos, load_amazon_products


# Allow HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create blueprint
main = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_info' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# OAuth 2.0 client configuration
client_secrets = {
    "web": {
        "client_id": Config.GOOGLE_CLIENT_ID,
        "project_id": "stylesnap-443901",  # Your project ID from Google Cloud
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
    }
}

@main.route('/')
def landing():
    """Route for landing page"""
    return render_template('landing.html')

@main.route('/camera')
def camera():
    """Route for camera page"""
    return render_template('camera.html')


@main.route('/results', methods=['GET', 'POST'])
def results():
    """Route for results page"""
    if request.method == 'POST':
        try:
            # Get or create user
            user = get_or_create_user()
            
            # Handle both file upload and camera capture
            filename = None
            photo_path = None
            
            if 'photo' in request.files:
                # Handle file upload
                file = request.files['photo']
                if file.filename != '':
                    filename = f"{uuid.uuid4()}.jpg"
                    photo_path = save_photo(file, filename)
                    
            elif 'photo' in request.form:
                # Handle camera capture
                photo_data = request.form.get('photo')
                if photo_data and photo_data.startswith('data:image/jpeg;base64,'):
                    filename = f"{uuid.uuid4()}.jpg"
                    photo_path = save_base64_photo(photo_data, filename)

            if photo_path:
                # Save to database and analyze
                analysis_results = save_and_analyze_photo(user.id, filename, photo_path)
                
                # Cleanup and return results
                cleanup_old_photos()
                return render_template('results.html', 
                                    photo_data=url_for('static', filename=f'photos/{filename}'), 
                                    analysis=analysis_results)

        except Exception as e:
            current_app.logger.error(f"Error in results route: {str(e)}")
            return redirect(url_for('main.camera'))

    return redirect(url_for('main.camera'))
                
    


@main.route('/login')
def login():
    """Route to initiate Google OAuth flow"""
    # Store the current page URL to redirect back after login
    session['next'] = request.args.get('next', url_for('main.dashboard'))
    
    flow = Flow.from_client_config(
        client_secrets,
        scopes=['https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'openid']
    )
    flow.redirect_uri = Config.GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@main.route('/oauth2callback')
def oauth2callback():
    """Callback route for Google OAuth"""
    try:
        flow = Flow.from_client_config(
            client_secrets,
            scopes=['https://www.googleapis.com/auth/userinfo.email',
                   'https://www.googleapis.com/auth/userinfo.profile',
                   'openid'],
            state=session['state']
        )
        flow.redirect_uri = Config.GOOGLE_REDIRECT_URI
        
        # Get full URL including query parameters
        authorization_response = request.url.replace('http://', 'https://')

        flow.fetch_token(authorization_response=authorization_response)
        
        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, requests.Request(), Config.GOOGLE_CLIENT_ID
        )
        
        session['user_info'] = {
            'email': id_info.get('email'),
            'name': id_info.get('name'),
            'picture': id_info.get('picture')
        }

        # Update or create user in database
        user = User.query.filter_by(email=id_info.get('email')).first()
        if user:
            # Update existing user's last login
            user.last_login = func.now()
        else:
            # Create new user
            user = User(
                email=id_info.get('email'),
                last_login=func.now(),
                subscription_status='free'
            )
            db.session.add(user)
        
        db.session.commit()
        
        # Redirect to the stored 'next' URL or main page
        next_page = session.pop('next', url_for('main.dashboard'))
        return redirect(next_page)
        
    except Exception as e:
        current_app.logger.error(f"OAuth error: {str(e)}")
        return redirect(url_for('main.landing'))

@main.route('/dashboard')
@login_required
def dashboard():
    """Route for main page after authentication"""

    # Load Amazon products
    amazon_products = load_amazon_products()

    return render_template('dashboard.html', 
                         user_info=session['user_info'],
                         last_photo=session.get('last_photo'),
                         products=amazon_products,
                         analysis=session.get('face_analysis'))


@main.route('/pricing')
def pricing():
    """Route for pricing page"""
    return render_template('settings/pricing.html')