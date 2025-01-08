""" utils.py - utility functions for routes.py"""
from flask import current_app, session, url_for
import json
import os
import uuid
import boto3
import base64

#db
from . import db
from .models import User, UserPhoto, FacialAnalysis

#AI
from .AI_utils import analyze_face

#AWS
from .s3_utils import upload_file_to_s3, delete_file_from_s3, get_s3_client


def load_amazon_products():
    """Load Amazon products from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'amazon_products.json')
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
            return data.get('products', [])
    except Exception as e:
        print(f"Error loading products: {e}")
        return []


def get_or_create_user():
    """Get existing user or create new one"""
    try:
        if not current_app:
            raise RuntimeError("No application context")
        
        # Start a new transaction
        db.session.begin_nested()
        
        if 'user_info' in session:
            user = User.query.filter_by(email=session['user_info']['email']).first()
            if not user:
                user = User(email=session['user_info']['email'])
                db.session.add(user)
        else:
            user = User(email=f'anonymous_{uuid.uuid4()}@temp.com')
            db.session.add(user)
        
        db.session.commit()
        return user
        
    except Exception as e:
        current_app.logger.error(f"Database error in get_or_create_user: {str(e)}")
        db.session.rollback()
        raise



def save_and_analyze_photo(user_id, file_data, is_base64=False):
    """Save photo to S3 and analyze it"""
    try:
        # Upload directly to S3
        current_app.logger.debug("Starting S3 upload...")
        s3_key, s3_url = upload_file_to_s3(file_data, user_id, is_base64)
        current_app.logger.debug(f"S3 upload complete. URL: {s3_url}")
        
        # Create photo record
        photo = UserPhoto(
            user_id=user_id,
            s3_key=s3_key,
            s3_url=s3_url,
            is_active=True
        )
        db.session.add(photo)
        db.session.flush()
        current_app.logger.debug(f"Photo record created with ID: {photo.id}")

        # Get the binary data for analysis
        if is_base64:
            # If it's base64 data, decode it
            if isinstance(file_data, str):
                if 'data:image' in file_data and 'base64,' in file_data:
                    file_data = file_data.split('base64,')[1]
                file_data = file_data.strip().replace('\n', '').replace('\r', '')
                image_data = base64.b64decode(file_data)
            else:
                raise ValueError("Base64 data must be a string")
        else:
            # If it's a file object, read it
            image_data = file_data.read()
            file_data.seek(0)  # Reset file pointer for S3 upload
        
        # Analyze directly from memory
        current_app.logger.debug("Starting face analysis...")
        analysis_results = analyze_face(image_data)
        current_app.logger.debug("Face analysis complete")
        
        # Save analysis results
        analysis = FacialAnalysis(
            user_id=user_id,
            photo_id=photo.id,
            analysis_data=analysis_results,
            score=analysis_results.get('score', 0)
        )
        db.session.add(analysis)
        db.session.commit()
        current_app.logger.debug("Analysis results saved to database")

        # Store in session
        session['last_photo'] = s3_url
        session['face_analysis'] = analysis_results
        current_app.logger.debug(f"Session updated with photo URL: {s3_url}")

        # Return both the analysis results and the photo URL
        result = {
            'analysis': analysis_results,
            'photo_url': s3_url
        }
        current_app.logger.debug(f"Returning result with photo URL: {s3_url}")
        return result
        
    except Exception as e:
        current_app.logger.error(f"Error in save_and_analyze_photo: {str(e)}")
        db.session.rollback()
        raise
