from flask import Blueprint, render_template

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def landing():
    """Route for landing page"""
    return render_template('landing.html')

@main.route('/camera')
def camera():
    """Route for camera page"""
    return render_template('camera.html')
