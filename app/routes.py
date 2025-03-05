import boto3
from botocore.config import Config as BotoConfig
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify, flash, send_file
from config import Config

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from functools import wraps
import uuid # for unique filename
from sqlalchemy.sql import func
#db
from . import db
from .models import User, UserPhoto, FacialAnalysis

#My utils
from .utils import get_or_create_user, save_and_analyze_photo, load_amazon_products



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

# Add this line to override the redirect URI with your ngrok URL
# Make sure this EXACTLY matches what's in your Google Cloud Console
NGROK_URL = "https://76fa-172-56-42-152.ngrok-free.app"  # Replace with your actual ngrok URL
REDIRECT_URI = f"{NGROK_URL}/oauth2callback"

@main.route('/')
def first():
    """Route for landing page"""
    return render_template('first.html')

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
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename != '':
                    result = save_and_analyze_photo(user.id, file, is_base64=False)
                    
            elif 'photo' in request.form:
                photo_data = request.form.get('photo')
                if photo_data and photo_data.startswith('data:image/jpeg;base64,'):
                    result = save_and_analyze_photo(user.id, photo_data, is_base64=True)
            
            if 'result' in locals():
                from botocore.config import Config as BotoConfig
                
                # Store config values in variables to avoid current_app access
                aws_access_key = Config.AWS_ACCESS_KEY_ID
                aws_secret_key = Config.AWS_SECRET_ACCESS_KEY
                bucket_name = Config.AWS_BUCKET_NAME
                
                s3_client = boto3.client('s3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name='us-east-2',
                    config=BotoConfig(
                        signature_version='s3v4'
                    )
                )
                
                # Get the key from the full URL
                key = result['photo_url'].replace(f'https://{bucket_name}.s3.us-east-2.amazonaws.com/', '')
                
                presigned_url = s3_client.generate_presigned_url('get_object',
                    Params={
                        'Bucket': bucket_name,
                        'Key': key
                    },
                    ExpiresIn=3600 # 1 hour
                )

                #Add presigned url to session
                session['photo_url'] = presigned_url
                
                return render_template('results.html', 
                                    photo_data=presigned_url,
                                    analysis=result['analysis'])
            else:
                return redirect(url_for('main.camera'))
                
        except Exception as e:
            import traceback
            print(f"Error in results route: {str(e)}")
            print(traceback.format_exc())  # This will print the full error traceback
            return redirect(url_for('main.camera'))

    return redirect(url_for('main.camera'))
                
    


@main.route('/login')
def login():
    """Route to initiate Google OAuth flow"""
    # Store the current page URL to redirect back after login
    session['next'] = request.args.get('next', url_for('main.dashboard'))
    
    # Debug information
    current_app.logger.info(f"Starting OAuth flow")
    current_app.logger.info(f"Using redirect URI: {REDIRECT_URI}")
    
    flow = Flow.from_client_config(
        client_secrets,
        scopes=['https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'openid']
    )
    # Override the redirect URI with the ngrok URL
    flow.redirect_uri = REDIRECT_URI
    current_app.logger.info(f"Flow redirect_uri: {flow.redirect_uri}")
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    current_app.logger.info(f"Authorization URL: {authorization_url}")
    
    session['state'] = state
    return redirect(authorization_url)

@main.route('/logout')
def logout():
    """Route to log out the user"""
    session.clear()
    return redirect(url_for('main.first'))

@main.route('/oauth2callback')
def oauth2callback():
    """Callback route for Google OAuth"""
    try:
        current_app.logger.info(f"OAuth callback received")
        current_app.logger.info(f"Request URL: {request.url}")
        
        flow = Flow.from_client_config(
            client_secrets,
            scopes=['https://www.googleapis.com/auth/userinfo.email',
                   'https://www.googleapis.com/auth/userinfo.profile',
                   'openid'],
            state=session['state']
        )
        # Use the same redirect URI as in the login route
        flow.redirect_uri = REDIRECT_URI
        current_app.logger.info(f"Flow redirect_uri: {flow.redirect_uri}")
        
        # Extract the query parameters from the request URL
        query_string = request.query_string.decode('utf-8')
        
        # Construct the authorization response using the ngrok URL
        authorization_response = f"{REDIRECT_URI}?{query_string}"
        current_app.logger.info(f"Constructed authorization response: {authorization_response}")
        
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
        return redirect(url_for('main.first'))

@main.route('/dashboard')
@login_required
def dashboard():
    """
    Route for main page after authentication
    Displays the user's latest photos and their analyses
    """
    # Get user from database
    user = User.query.filter_by(email=session['user_info']['email']).first()
    
    # Initialize variables for photos and analyses
    latest_photos = []
    photo_analyses = {}
    
    if user:
        # Query for the three latest photos
        latest_photos = UserPhoto.query.filter_by(
            user_id=user.id, 
            is_active=True
        ).order_by(
            UserPhoto.upload_date.desc()
        ).limit(3).all()
        
        # Get the analysis for each photo
        for photo in latest_photos:
            analysis = FacialAnalysis.query.filter_by(photo_id=photo.id).first()
            if analysis:
                photo_analyses[photo.id] = analysis
    
    # For debugging
    current_app.logger.debug(f"Found {len(latest_photos)} photos for user {user.email if user else 'unknown'}")
    for i, photo in enumerate(latest_photos):
        current_app.logger.debug(f"Photo {i+1}: ID={photo.id}, Date={photo.upload_date}")
        if photo.id in photo_analyses:
            current_app.logger.debug(f"  Analysis found: Score={photo_analyses[photo.id].score}")
        else:
            current_app.logger.debug(f"  No analysis found")
    
    # Load Amazon products
    amazon_products = load_amazon_products()

    return render_template('dashboard.html', 
                         user_info=session['user_info'],
                         photo_url=session.get('photo_url'),
                         latest_photos=latest_photos,
                         photo_analyses=photo_analyses,
                         products=amazon_products,
                         analysis=session.get('face_analysis'))


@main.route('/home')
@login_required
def home():
    """Route for home page"""
    return render_template('home.html',
                           user_info=session['user_info'],
                           photo_url=session.get('photo_url'),
                           analysis=session.get('face_analysis'))
@main.route('/pricing')
def pricing():
    """Route for pricing page"""
    return render_template('settings/pricing.html')



@main.route('/landing')
def landing():
    """Route for landing page"""
    return render_template('landing.html')

@main.route('/photo/<int:photo_id>')
@login_required
def get_photo(photo_id):
    """Proxy route to serve S3 photos with proper authentication"""
    try:
        # Get user from session
        user_email = session['user_info']['email']
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            current_app.logger.error(f"User not found: {user_email}")
            return jsonify({"error": "User not found"}), 404
        
        # Get the photo, ensuring it belongs to the current user
        photo = UserPhoto.query.filter_by(id=photo_id, user_id=user.id).first()
        
        if not photo:
            current_app.logger.error(f"Photo not found or doesn't belong to user: {photo_id}")
            return jsonify({"error": "Photo not found"}), 404
        
        # Initialize S3 client
        s3_client = boto3.client('s3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION,
            config=BotoConfig(
                signature_version='s3v4'
            )
        )
        
        # Generate a presigned URL for the S3 object
        presigned_url = s3_client.generate_presigned_url('get_object',
            Params={
                'Bucket': Config.AWS_BUCKET_NAME,
                'Key': photo.s3_key
            },
            ExpiresIn=3600  # 1 hour
        )
        
        # Return the presigned URL as JSON
        return jsonify({"url": presigned_url})
    except Exception as e:
        current_app.logger.error(f"Error in get_photo route: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500