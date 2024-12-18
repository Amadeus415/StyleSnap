
from flask import current_app, session

#db
from . import db
from .models import User, UserPhoto, FacialAnalysis

# functions
import json
import os
import uuid
import base64
from flask import current_app, session, url_for


#AI
from .AI_utils import analyze_face

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
    

def cleanup_old_photos():
    """Cleanup old photos from static/photos directory except for current one"""
    photos_dir = os.path.join(current_app.static_folder, 'photos')
    current_photo = session.get('last_photo')
    if current_photo:
        # Remove all photos except the current one
        for filename in os.listdir(photos_dir):
            if filename != os.path.basename(current_photo):
                os.remove(os.path.join(photos_dir, filename))



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

def save_photo(file, filename):
    """Save uploaded file"""
    photo_path = os.path.join(current_app.static_folder, 'photos', filename)
    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
    file.save(photo_path)
    return photo_path

def save_base64_photo(photo_data, filename):
    """Save base64 photo data"""
    photo_path = os.path.join(current_app.static_folder, 'photos', filename)
    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
    
    photo_data = photo_data.split(',')[1]
    with open(photo_path, 'wb') as f:
        f.write(base64.b64decode(photo_data))
    return photo_path

def save_and_analyze_photo(user_id, filename, photo_path):
    """Save photo to database and run analysis"""
    # Create photo record
    photo = UserPhoto(
        user_id=user_id,
        s3_key=filename,
        is_active=True
    )
    db.session.add(photo)
    db.session.flush()

    # Analyze and save results
    analysis_results = analyze_face(photo_path)
    analysis = FacialAnalysis(
        user_id=user_id,
        photo_id=photo.id,
        analysis_data=analysis_results,
        score=analysis_results.get('score', 0)
    )
    db.session.add(analysis)
    db.session.commit()

    # Store in session
    session['last_photo'] = url_for('static', filename=f'photos/{filename}')
    session['face_analysis'] = analysis_results

    return analysis_results
