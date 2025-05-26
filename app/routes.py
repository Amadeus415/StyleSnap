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
from .AI_utils import analyze_face, generate_tailored_plan

import json

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
NGROK_URL = "https://14d1-2607-fb90-9e99-ad3-9df4-6009-4d47-2d9.ngrok-free.app"  # Replace with your actual ngrok URL
REDIRECT_URI = f"{NGROK_URL}/oauth2callback"

@main.route('/')
def home():
    """Route for landing page"""
    return render_template('home.html')

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

                #If user is logged in, save photo to database and redirect to dashboard
                if 'user_info' in session:
                    # User is logged in, redirect to dashboard
                    return redirect(url_for('main.dashboard'))
                else:
                    # User is not logged in, show results page
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
    return redirect(url_for('main.home'))

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
            db.session.flush()  # Flush to get the user ID
        
        # Check if there's a photo in the session that needs to be transferred
        # from an anonymous user to this authenticated user
        try:
            # Try to get the photo URL from either session key
            photo_url = session.get('last_photo') or session.get('photo_url')
            
            if photo_url:
                current_app.logger.info(f"Found photo URL in session: {photo_url}")
                # Find the photo in the database
                photo = UserPhoto.query.filter_by(s3_url=photo_url).first()
                
                if not photo:
                    # If we can't find by s3_url, try to extract the key from the URL
                    bucket_name = Config.AWS_BUCKET_NAME
                    if f"{bucket_name}.s3" in photo_url:
                        key = photo_url.split(f"{bucket_name}.s3")[1].split('/', 1)[1]
                        photo = UserPhoto.query.filter_by(s3_key=key).first()
                
                if photo:
                    # Get the owner of the photo
                    photo_owner = User.query.get(photo.user_id)
                    
                    # If the photo exists and belongs to an anonymous user, transfer it
                    if photo_owner and 'anonymous' in photo_owner.email:
                        # Transfer the photo to the authenticated user
                        photo.user_id = user.id
                        
                        # Also transfer any analysis data
                        analysis = FacialAnalysis.query.filter_by(photo_id=photo.id).first()
                        if analysis:
                            analysis.user_id = user.id
                        
                        current_app.logger.info(f"Transferred photo {photo.id} from anonymous user to {user.email}")
        except Exception as e:
            current_app.logger.error(f"Error transferring photo: {str(e)}")
        
        db.session.commit()
        
        # Redirect to the stored 'next' URL or main page
        next_page = session.pop('next', url_for('main.dashboard'))
        return redirect(next_page)
        
    except Exception as e:
        current_app.logger.error(f"OAuth error: {str(e)}")
        return redirect(url_for('main.home'))

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
    products = load_amazon_products()
    amazon_products = {'products': products}

    # If we have a photo URL in the session but no photos were found,
    # this might be a race condition where the photo transfer just happened
    # but the query above didn't catch it. Let's check again.
    if len(latest_photos) == 0 and ('photo_url' in session or 'last_photo' in session):
        photo_url = session.get('last_photo') or session.get('photo_url')
        if photo_url:
            # Try to find the photo directly
            photo = UserPhoto.query.filter_by(s3_url=photo_url, user_id=user.id).first()
            if photo:
                latest_photos = [photo]
                analysis = FacialAnalysis.query.filter_by(photo_id=photo.id).first()
                if analysis:
                    photo_analyses[photo.id] = analysis
                    
                current_app.logger.debug(f"Found photo by URL: ID={photo.id}")

    return render_template('dashboard.html', 
                         user_info=session['user_info'],
                         photo_url=session.get('photo_url'),
                         latest_photos=latest_photos,
                         photo_analyses=photo_analyses,
                         amazon_products=amazon_products,
                         analysis=session.get('face_analysis'))


# @main.route('/home')
# def home():
#     """Route for home page"""
#     return render_template('home.html')


@main.route('/test')
def test():
    """Route for test page"""
    return render_template('test.html')


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

@main.route('/photo_popup/<int:photo_id>')
@login_required
def photo_popup(photo_id):
    """
    Route to render the photo popup template with complete analysis data
    
    This route:
    1. Retrieves the photo data for the specified ID
    2. Ensures the photo belongs to the current user
    3. Fetches the associated analysis data
    4. Generates a presigned URL for the photo
    5. Renders the popup template with all data
    
    Args:
        photo_id (int): The ID of the photo to display
        
    Returns:
        Rendered HTML template with all photo analysis data
    """
    try:
        # Get user from session
        user_email = session['user_info']['email']
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            current_app.logger.error(f"User not found: {user_email}")
            return "User not found", 404
        
        # Get the photo, ensuring it belongs to the current user
        photo = UserPhoto.query.filter_by(id=photo_id, user_id=user.id).first()
        
        if not photo:
            current_app.logger.error(f"Photo not found or doesn't belong to user: {photo_id}")
            return "Photo not found", 404
        
        # Get the analysis for the photo
        analysis = FacialAnalysis.query.filter_by(photo_id=photo.id).first()
        
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
        
        # Prepare template data
        template_data = {
            "photo_id": photo.id,
            "photo_url": presigned_url,
            "upload_date": photo.upload_date.strftime('%b %d, %Y'),
        }
        
        # If analysis exists, add the analysis data to the template
        if analysis:
            # Convert analysis_data from JSON string if needed
            analysis_data = analysis.analysis_data
            if isinstance(analysis_data, str):
                try:
                    analysis_data = json.loads(analysis_data)
                except json.JSONDecodeError:
                    analysis_data = {}
            
            template_data["analysis_data"] = analysis_data
        else:
            # Provide empty analysis data if none exists
            template_data["analysis_data"] = {}
        
        # Render only the popup template content
        return render_template('partials/photo_popup.html', **template_data)
    except Exception as e:
        current_app.logger.error(f"Error in photo_popup route: {str(e)}")
        return "An error occurred", 500

@main.route('/generate_tailored_plan', methods=['POST'])
@login_required
def get_tailored_plan():
    """
    API endpoint to generate a tailored plan based on the user's latest analysis
    """
    try:
        # Get user from session
        user_email = session['user_info']['email']
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get the latest photo analysis
        latest_analysis = FacialAnalysis.query.filter_by(
            user_id=user.id
        ).order_by(
            FacialAnalysis.created_at.desc()
        ).first()
        
        if not latest_analysis:
            return jsonify({"error": "No analysis found for this user"}), 404
        
        # Get the analysis data
        analysis_data = latest_analysis.analysis_data
        if isinstance(analysis_data, str):
            try:
                analysis_data = json.loads(analysis_data)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid analysis data format"}), 500
        
        # Load available products
        products = load_amazon_products()
        
        # Generate tailored plan
        tailored_plan = generate_tailored_plan(analysis_data, products)
        
        # Return the tailored plan as JSON
        return jsonify(tailored_plan)
    
    except Exception as e:
        current_app.logger.error(f"Error in generate_tailored_plan route: {str(e)}")
        return jsonify({"error": str(e)}), 500