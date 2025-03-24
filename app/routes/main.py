from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route."""
    current_app.logger.info(f"User {current_user.username} accessed dashboard")
    return render_template('main/dashboard.html')
