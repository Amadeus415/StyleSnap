from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON
from . import db  # Import db from __init__.py directly

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    subscription_status = db.Column(db.String(20), default='free')  # 'free', 'premium', 'expired'
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship with photos
    photos = db.relationship('UserPhoto', backref='user', lazy=True)

class UserPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    s3_key = db.Column(db.String(200), nullable=False)  # e.g., "users/123/profile.jpg"
    upload_date = db.Column(db.DateTime, default=func.now())
    is_active = db.Column(db.Boolean, default=True)


class FacialAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('user_photo.id'), nullable=False)
    analysis_data = db.Column(JSON, nullable=False)  # Stores AI output
    created_at = db.Column(db.DateTime, default=func.now())
    score = db.Column(db.Float)  # Optional: store main score for easy querying
    
    # Relationships
    user = db.relationship('User', backref='analyses')
    photo = db.relationship('UserPhoto', backref='analysis')