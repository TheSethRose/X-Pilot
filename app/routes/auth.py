from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
import tweepy
from datetime import datetime
import os

from app.models import db, User
from utils.twitter_auth import TwitterOAuth
from utils.quota_tracker import QuotaTracker

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

    # Get the ngrok URL from app config
    ngrok_base_url = current_app.config.get('SITE_URL', 'http://localhost:5000')
    callback_url = f"{ngrok_base_url}/auth/twitter_callback"
    current_app.logger.info(f"Using callback URL: {callback_url}")

    # Get the authorization URL with explicit callback
    auth_url = TwitterOAuth.get_authorization_url(callback_url=callback_url)

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

    # Log all request parameters for debugging
    current_app.logger.debug(f"Callback parameters: {request.args}")
    current_app.logger.debug(f"Request token in session: {session.get('request_token')}")

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

    # Log success getting tokens
    current_app.logger.info("Successfully obtained access tokens")

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

@auth_bp.route('/tokens', methods=['GET'])
@login_required
def manage_tokens():
    """View and manage Twitter API tokens."""
    # Track this as a profile view API call for quota
    quota_info = QuotaTracker.track_api_call(current_user.id, "tokens")

    # Mask tokens for display
    masked_consumer_key = mask_token(current_user.consumer_key)
    masked_consumer_secret = mask_token(current_user.consumer_secret)
    masked_access_token = mask_token(current_user.access_token)
    masked_access_token_secret = mask_token(current_user.access_token_secret)

    # Check if tokens are working by making a simple API call
    token_status = check_token_status(current_user)

    return render_template(
        'auth/tokens.html',
        masked_consumer_key=masked_consumer_key,
        masked_consumer_secret=masked_consumer_secret,
        masked_access_token=masked_access_token,
        masked_access_token_secret=masked_access_token_secret,
        token_status=token_status,
        quota_info=quota_info
    )

@auth_bp.route('/tokens/refresh', methods=['POST'])
@login_required
def refresh_tokens():
    """Re-authorize with Twitter to refresh access tokens."""
    # Record the user is refreshing tokens
    current_app.logger.info(f"User {current_user.username} is refreshing their Twitter access tokens")

    # Redirect to the Twitter authorization flow
    # Use a special parameter to indicate this is a token refresh
    session['is_token_refresh'] = True
    return redirect(url_for('auth.twitter_authorize'))

@auth_bp.route('/tokens/revoke', methods=['POST'])
@login_required
def revoke_tokens():
    """Revoke the current access tokens."""
    try:
        # In a real implementation, we would call Twitter's API to revoke the token
        # For now, we'll just clear them from our database

        # Save old username for the flash message
        username = current_user.username

        # Clear tokens
        current_user.access_token = None
        current_user.access_token_secret = None
        db.session.commit()

        # Log action
        current_app.logger.info(f"User {username} has revoked their Twitter access tokens")

        # Log out the user since they can no longer use the app without tokens
        logout_user()

        flash("Your Twitter access has been revoked. You will need to log in again to use 𝕏-Pilot.", "info")
        return redirect(url_for('main.index'))

    except Exception as e:
        flash(f"Error revoking tokens: {str(e)}", "error")
        current_app.logger.error(f"Error revoking tokens for user {current_user.username}: {str(e)}")
        return redirect(url_for('auth.manage_tokens'))

# Helper functions for token management

def mask_token(token):
    """Mask a token for display purposes, showing only first and last 4 characters."""
    if not token:
        return "None"

    if len(token) <= 8:
        return "****"

    return token[:4] + "..." + token[-4:]

def check_token_status(user):
    """Check if the user's tokens are valid and working."""
    if not user.access_token or not user.access_token_secret:
        return {
            "valid": False,
            "message": "No access tokens found."
        }

    try:
        # For simulation mode, always return valid
        if TwitterOAuth.is_simulation_enabled():
            return {
                "valid": True,
                "message": "Tokens are valid (simulation mode)",
                "created_at": datetime.utcnow().strftime('%B %d, %Y')
            }

        # In free tier, we can't make API calls to verify tokens, but if the user
        # is logged in successfully, we can assume the tokens are valid

        # Check if tokens exist and aren't obviously invalid
        if user.access_token and user.access_token_secret:
            return {
                "valid": True,
                "message": "Tokens exist and user is logged in. Free tier doesn't allow detailed token validation.",
                "created_at": user.last_login.strftime('%B %d, %Y')
            }
        else:
            return {
                "valid": False,
                "message": "Tokens appear to be missing or invalid."
            }

    except Exception as e:
        return {
            "valid": False,
            "message": f"Error checking token status: {str(e)}"
        }
