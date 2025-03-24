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
        # Get client
        api_client = TwitterOAuth.get_api_client(
            current_user.access_token,
            current_user.access_token_secret
        )

        # Track this API call for quota
        quota_info = QuotaTracker.track_api_call(current_user.id, "profile")

        # Get user info from Twitter
        if not TwitterOAuth.is_simulation_enabled():
            user_info = api_client.get_user(username=current_user.username)
            profile_data = {
                'following_count': user_info.following_count,
                'followers_count': user_info.followers_count,
                'tweet_count': user_info.tweet_count,
                'created_at': user_info.created_at,
                'description': user_info.description
            }
        else:
            # Use simulated data in development mode
            profile_data = {
                'following_count': 421,
                'followers_count': 152,
                'tweet_count': 1024,
                'created_at': datetime.utcnow(),
                'description': "This is a simulated user description for development purposes."
            }

        return render_template('users/profile.html',
                              profile_data=profile_data,
                              quota_info=quota_info)

    except Exception as e:
        current_app.logger.error(f"Error fetching profile data: {str(e)}")
        flash(f"Error fetching profile data: {str(e)}", 'error')
        # Return basic profile without Twitter data
        return render_template('users/profile.html')

@users_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Search for 𝕏 users."""
    users = []
    searched = False

    if request.method == 'POST':
        query = request.form.get('query', '')
        if not query:
            flash('Please enter a search term', 'warning')
            return redirect(url_for('users.search'))

        searched = True
        try:
            # Get client
            api_client = TwitterOAuth.get_api_client(
                current_user.access_token,
                current_user.access_token_secret
            )

            # Track this API call for quota
            quota_info = QuotaTracker.track_api_call(current_user.id, "search")

            if not TwitterOAuth.is_simulation_enabled():
                # Get user search results from Twitter
                search_results = api_client.search_users(q=query, count=10)

                for user in search_results:
                    users.append({
                        'id': user.id,
                        'name': user.name,
                        'username': user.screen_name,
                        'profile_image_url': user.profile_image_url_https,
                        'description': user.description,
                        'followers_count': user.followers_count,
                        'following_count': user.friends_count
                    })
            else:
                # Simulated data for development
                users = [
                    {
                        'id': 123456,
                        'name': 'Elon Musk',
                        'username': 'elonmusk',
                        'profile_image_url': 'https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg',
                        'description': 'Technoking of Tesla, Chief Twit of Twitter',
                        'followers_count': 128500000,
                        'following_count': 177
                    },
                    {
                        'id': 789012,
                        'name': 'Twitter',
                        'username': 'Twitter',
                        'profile_image_url': 'https://pbs.twimg.com/profile_images/1683899100922511378/5lY42eHs_400x400.jpg',
                        'description': 'What\'s happening?!',
                        'followers_count': 67800000,
                        'following_count': 5
                    }
                ]

                # Filter simulated data based on query
                users = [u for u in users if query.lower() in u['name'].lower() or query.lower() in u['username'].lower()]

            current_app.logger.info(f"User {current_user.username} searched for '{query}', found {len(users)} results")

        except Exception as e:
            current_app.logger.error(f"Error searching for users: {str(e)}")
            flash(f"Error searching for users: {str(e)}", 'error')

    return render_template('users/search.html', users=users, searched=searched)

@users_bp.route('/<username>/view')
@login_required
def view(username):
    """View another user's profile."""
    try:
        # Get client
        api_client = TwitterOAuth.get_api_client(
            current_user.access_token,
            current_user.access_token_secret
        )

        # Track this API call for quota
        quota_info = QuotaTracker.track_api_call(current_user.id, "profile_view")

        if not TwitterOAuth.is_simulation_enabled():
            # Get user info from Twitter
            user_info = api_client.get_user(username=username)

            user = {
                'id': user_info.id,
                'name': user_info.name,
                'username': user_info.screen_name,
                'profile_image_url': user_info.profile_image_url_https,
                'description': user_info.description,
                'followers_count': user_info.followers_count,
                'following_count': user_info.friends_count,
                'tweet_count': user_info.statuses_count,
                'created_at': user_info.created_at,
                'location': user_info.location,
                'verified': user_info.verified
            }
        else:
            # Simulated data
            user = {
                'id': 123456,
                'name': 'Elon Musk' if username.lower() == 'elonmusk' else f"User {username}",
                'username': username,
                'profile_image_url': 'https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg',
                'description': 'This is a simulated user profile for development.',
                'followers_count': 128500000,
                'following_count': 177,
                'tweet_count': 25000,
                'created_at': datetime.utcnow(),
                'location': 'Mars',
                'verified': True
            }

        # Check if the current user is following this user
        is_following = False
        if not TwitterOAuth.is_simulation_enabled():
            # This would be an actual API call to check the relationship
            # The API method will depend on the version of the Twitter API you're using
            pass
        else:
            # Simulated following status (randomly true or false)
            import random
            is_following = random.choice([True, False])

        return render_template('users/view.html', user=user, is_following=is_following, quota_info=quota_info)

    except Exception as e:
        current_app.logger.error(f"Error viewing user profile: {str(e)}")
        flash(f"Error viewing user profile: {str(e)}", 'error')
        return redirect(url_for('users.search'))

@users_bp.route('/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    """Follow a 𝕏 user."""
    try:
        # Get client
        api_client = TwitterOAuth.get_api_client(
            current_user.access_token,
            current_user.access_token_secret
        )

        # Track this API call for quota
        quota_info = QuotaTracker.track_api_call(current_user.id, "follow")

        if not TwitterOAuth.is_simulation_enabled():
            # Follow user on Twitter
            api_client.create_friendship(screen_name=username)

        flash(f"You are now following @{username}", 'success')
        current_app.logger.info(f"User {current_user.username} is now following {username}")

    except Exception as e:
        current_app.logger.error(f"Error following user: {str(e)}")
        flash(f"Error following user: {str(e)}", 'error')

    # Redirect back to the user's profile
    return redirect(url_for('users.view', username=username))

@users_bp.route('/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    """Unfollow a 𝕏 user."""
    try:
        # Get client
        api_client = TwitterOAuth.get_api_client(
            current_user.access_token,
            current_user.access_token_secret
        )

        # Track this API call for quota
        quota_info = QuotaTracker.track_api_call(current_user.id, "unfollow")

        if not TwitterOAuth.is_simulation_enabled():
            # Unfollow user on Twitter
            api_client.destroy_friendship(screen_name=username)

        flash(f"You have unfollowed @{username}", 'success')
        current_app.logger.info(f"User {current_user.username} has unfollowed {username}")

    except Exception as e:
        current_app.logger.error(f"Error unfollowing user: {str(e)}")
        flash(f"Error unfollowing user: {str(e)}", 'error')

    # Redirect back to the user's profile
    return redirect(url_for('users.view', username=username))
