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

        # We can access our own user information in the free tier
        # Initialize with bearer token
        bearer_token = os.environ.get('BEARER_TOKEN')

        # Use data from our database initially, may be updated with API data
        profile_data = {
            'following_count': 0,
            'followers_count': 0,
            'tweet_count': len(current_user.tweets) if current_user.tweets else 0,
            'created_at': current_user.last_login or datetime.utcnow(),
            'description': f"Profile for @{current_user.username}",
            'username': current_user.username,
            'name': current_user.name,
            'profile_image_url': current_user.profile_image_url
        }

        if not bearer_token:
            current_app.logger.error("Missing BEARER_TOKEN in environment")
            flash("Missing API credentials. Check your .env file.", "error")
            return render_template('users/profile.html',
                                  profile_data=profile_data,
                                  quota_info=quota_info)

        try:
            # Try to get updated data from Twitter
            import tweepy
            client = tweepy.Client(bearer_token=bearer_token)

            # This will fetch user data from Twitter, which should work in the free tier
            current_app.logger.debug(f"Attempting to fetch user data for {current_user.username}")

            # Following tweepy's client.get_user documentation format
            user_data = client.get_user(
                username=current_user.username,
                user_fields=["description", "created_at", "profile_image_url", "public_metrics"]
            )

            # Log the response structure to debug
            current_app.logger.debug(f"User data response: {user_data}")

            # If we successfully got data, update our profile_data
            if user_data and hasattr(user_data, 'data') and user_data.data:
                user = user_data.data
                current_app.logger.info(f"Successfully fetched profile data for {current_user.username}")

                # Try to extract metrics if they exist
                try:
                    metrics = {}
                    if hasattr(user, 'public_metrics'):
                        metrics = user.public_metrics

                    # Update profile data with real metrics from Twitter
                    profile_data.update({
                        'following_count': metrics.get('following_count', 0),
                        'followers_count': metrics.get('followers_count', 0),
                        'tweet_count': metrics.get('tweet_count', 0),
                        'created_at': getattr(user, 'created_at', profile_data['created_at']),
                        'description': getattr(user, 'description', profile_data['description'])
                    })
                except Exception as metrics_error:
                    current_app.logger.error(f"Error extracting metrics: {metrics_error}")

        except Exception as api_error:
            current_app.logger.error(f"Error fetching profile from Twitter API: {str(api_error)}")
            # We'll just use the database profile data initialized above

        return render_template('users/profile.html',
                              profile_data=profile_data,
                              quota_info=quota_info)

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
