from flask import Blueprint, render_template, request, redirect, url_for

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

@main.route('/results', methods=['GET', 'POST'])
def results():
    """Route for results page"""
    if request.method == 'POST':
        photo_data = request.form.get('photo')
        if photo_data:
            return render_template('results.html', photo_data=photo_data)
    return redirect(url_for('main.camera'))
