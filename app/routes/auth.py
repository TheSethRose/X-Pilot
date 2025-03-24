from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
import tweepy
from datetime import datetime
import os

from app.models import db, User
from utils.twitter_auth import TwitterOAuth

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        return redirect(url_for('auth.twitter_authorize'))

    return render_template('auth/login.html')

@auth_bp.route('/twitter_authorize')
def twitter_authorize():
    """Redirect to Twitter for authorization."""
    current_app.logger.info("Redirecting to Twitter for authorization")

    # First check if the Twitter credentials are configured
    if not current_app.config.get('TWITTER_CONSUMER_KEY') or not current_app.config.get('TWITTER_CONSUMER_SECRET'):
        flash('Twitter API credentials are not configured. Please check your .env file.', 'error')
        current_app.logger.error("Twitter API credentials missing")
        return redirect(url_for('main.index'))

    # For full simulation mode
    if TwitterOAuth.is_simulation_enabled():
        current_app.logger.info("Using simulation mode, redirecting directly to callback")
        # Directly redirect to the callback with a fake verifier
        return redirect(url_for('auth.twitter_callback') + '?oauth_verifier=fake_verifier')

    # Get the authorization URL
    auth_url = TwitterOAuth.get_authorization_url()

    if not auth_url:
        flash('Error connecting to Twitter API. Please check your credentials and try again.', 'error')
        current_app.logger.error("Failed to get Twitter authorization URL")
        return redirect(url_for('main.index'))

    current_app.logger.info(f"Redirecting to Twitter auth URL: {auth_url[:30]}...")
    return redirect(auth_url)

@auth_bp.route('/twitter_callback')
def twitter_callback():
    """Handle callback from Twitter OAuth."""
    current_app.logger.info("Received callback from Twitter OAuth")

    # Check for denied access - not applicable in simulation
    if not TwitterOAuth.is_simulation_enabled():
        denied = request.args.get('denied')
        if denied:
            flash('Twitter authorization was denied.', 'error')
            return redirect(url_for('main.index'))

    # Get OAuth verifier from the callback parameters or use fake one
    oauth_verifier = request.args.get('oauth_verifier', 'fake_verifier')
    if not oauth_verifier and not TwitterOAuth.is_simulation_enabled():
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('main.index'))

    # Get access tokens
    tokens = TwitterOAuth.get_access_token(oauth_verifier)
    if not tokens:
        flash('Failed to obtain access tokens. Please try again.', 'error')
        return redirect(url_for('main.index'))

    # Get user info from Twitter
    user_info = TwitterOAuth.get_user_info(
        tokens['access_token'],
        tokens['access_token_secret']
    )

    if not user_info:
        flash('Failed to get user information from Twitter.', 'error')
        return redirect(url_for('main.index'))

    # Check if user exists, otherwise create a new one
    user = User.query.filter_by(twitter_id=user_info['twitter_id']).first()

    if user:
        # Update existing user
        user.username = user_info['username']
        user.name = user_info['name']
        user.profile_image_url = user_info['profile_image_url']
        user.access_token = tokens['access_token']
        user.access_token_secret = tokens['access_token_secret']
        user.last_login = datetime.utcnow()
    else:
        # Create a new user - use direct attributes instead of named parameters
        user = User()
        user.twitter_id = user_info['twitter_id']
        user.username = user_info['username']
        user.name = user_info['name']
        user.profile_image_url = user_info['profile_image_url']
        user.consumer_key = current_app.config['TWITTER_CONSUMER_KEY']
        user.consumer_secret = current_app.config['TWITTER_CONSUMER_SECRET']
        user.access_token = tokens['access_token']
        user.access_token_secret = tokens['access_token_secret']
        user.last_login = datetime.utcnow()
        db.session.add(user)

    # Save changes to database
    db.session.commit()

    # Log in the user
    login_user(user)
    flash(f'Welcome, @{user.username}!', 'success')

    # Clear session
    if 'request_token' in session:
        del session['request_token']

    return redirect(url_for('main.dashboard'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
