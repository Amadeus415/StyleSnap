# functions
import json
import os

from flask import current_app, session

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

