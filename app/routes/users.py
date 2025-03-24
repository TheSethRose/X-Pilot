from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
import tweepy
from datetime import datetime
import os

from app.models import db, User
from utils.twitter_auth import TwitterOAuth
from utils.quota_tracker import QuotaTracker

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/profile')
@login_required
def profile():
    """Display the current user's profile with updated statistics from Twitter."""
    try:
        # Track this API call for quota
        quota_info = QuotaTracker.track_api_call(current_user.id, "profile")

        # IMPORTANT: Free tier does not allow user lookups, so we'll always use simulated data
        # or data from our database instead of making API calls
        profile_data = {
            'following_count': 0,  # We'll use values from our database where possible
            'followers_count': 0,
            'tweet_count': 0,
            'created_at': current_user.last_login or datetime.utcnow(),
            'description': "Profile data unavailable in free tier - this user data is from our local database.",
            'username': current_user.username,
            'name': current_user.name,
            'profile_image_url': current_user.profile_image_url
        }

        current_app.logger.info(f"Using local profile data for user {current_user.username}")
        return render_template('users/profile.html',
                              profile_data=profile_data,
                              quota_info=quota_info,
                              free_tier_message="Note: User profile data from X API is limited in the free tier.")

    except Exception as e:
        current_app.logger.error(f"Error preparing profile data: {str(e)}")
        flash(f"Error preparing profile data: {str(e)}", 'error')
        # Return basic profile without any data
        return render_template('users/profile.html')

@users_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Search for 𝕏 users."""
    # User search is not available in free tier
    flash("User search is not available in the X API free tier. Please upgrade to a paid tier for this functionality.", "info")
    current_app.logger.info(f"User {current_user.username} attempted to search for users (not available in free tier)")

    return render_template('users/search.html', users=[], searched=False,
                          free_tier_message="User search is not available in the X API free tier.")

@users_bp.route('/<username>/view')
@login_required
def view(username):
    """View another user's profile."""
    # Viewing other users is not available in free tier
    flash("Viewing user profiles is not available in the X API free tier. Please upgrade to a paid tier for this functionality.", "info")
    current_app.logger.info(f"User {current_user.username} attempted to view profile of {username} (not available in free tier)")

    return render_template('users/search.html', users=[], searched=False,
                          free_tier_message="Viewing user profiles is not available in the X API free tier.")

@users_bp.route('/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    """Follow a 𝕏 user."""
    # Following users is not available in free tier
    flash("Following users is not available in the X API free tier. Please upgrade to a paid tier for this functionality.", "info")
    current_app.logger.info(f"User {current_user.username} attempted to follow {username} (not available in free tier)")

    return redirect(url_for('main.dashboard'))

@users_bp.route('/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    """Unfollow a 𝕏 user."""
    # Unfollowing users is not available in free tier
    flash("Unfollowing users is not available in the X API free tier. Please upgrade to a paid tier for this functionality.", "info")
    current_app.logger.info(f"User {current_user.username} attempted to unfollow {username} (not available in free tier)")

    return redirect(url_for('main.dashboard'))
