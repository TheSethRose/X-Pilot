from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
import tweepy
from datetime import datetime

from app.models import db, Post
from utils.quota_tracker import QuotaTracker

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/')
@login_required
def index():
    """List user's posts."""
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    # Get quota information for the user
    quota_status = QuotaTracker.get_quota_status(current_user)
    return render_template('posts/index.html', posts=posts, quota=quota_status)

@posts_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    """Compose and post a new post."""
    if request.method == 'POST':
        text = request.form.get('text', '').strip()

        if not text:
            flash('Post content cannot be empty.', 'error')
            return render_template('posts/compose.html', text='')

        # Check if user has X Premium/Blue (verified) to determine character limit
        # X Premium/Blue users can post up to 4000/10000 characters depending on their tier
        # Regular users are limited to 280 characters
        is_premium_user = current_user.is_verified or current_user.verified_type in ['Business', 'Government', 'Blue']
        char_limit = 4000 if is_premium_user else 280

        if len(text) > char_limit:
            flash(f'Post exceeds {char_limit} character limit for your account type.', 'error')
            return render_template('posts/compose.html', text=text, premium=is_premium_user, char_limit=char_limit)

        # Check if scheduling is requested
        schedule_checkbox = request.form.get('schedule')
        schedule_date = request.form.get('schedule_date')
        schedule_time = request.form.get('schedule_time')

        if schedule_checkbox and schedule_date and schedule_time:
            # Create a scheduled post
            try:
                scheduled_at = datetime.strptime(f"{schedule_date} {schedule_time}", "%Y-%m-%d %H:%M")

                if scheduled_at <= datetime.utcnow():
                    flash('Scheduled time must be in the future.', 'error')
                    return render_template('posts/compose.html',
                                          text=text,
                                          premium=is_premium_user,
                                          char_limit=char_limit)

                # Create a scheduled post
                post = Post()
                post.user_id = current_user.id
                post.text = text
                post.status = 'scheduled'
                post.scheduled_at = scheduled_at
                db.session.add(post)
                db.session.commit()

                flash('Post scheduled successfully!', 'success')
                return redirect(url_for('posts.scheduled'))

            except ValueError:
                flash('Invalid date or time format.', 'error')
                return render_template('posts/compose.html',
                                      text=text,
                                      premium=is_premium_user,
                                      char_limit=char_limit)
        else:
            # Post post immediately
            try:
                # Check quota before posting
                quota_status = QuotaTracker.get_quota_status(current_user)

                if quota_status['posts_used'] >= quota_status['monthly_limit']:
                    flash('API quota limit reached. Cannot post.', 'error')
                    return render_template('posts/compose.html',
                                          text=text,
                                          quota=quota_status,
                                          premium=is_premium_user,
                                          char_limit=char_limit)

                # Post to Twitter
                auth = tweepy.OAuth1UserHandler(
                    current_user.consumer_key,
                    current_user.consumer_secret,
                    current_user.access_token,
                    current_user.access_token_secret
                )

                # Use v2 Client instead of v1.1 API
                client = tweepy.Client(
                    consumer_key=current_user.consumer_key,
                    consumer_secret=current_user.consumer_secret,
                    access_token=current_user.access_token,
                    access_token_secret=current_user.access_token_secret
                )

                # Use create_post method from v2 API instead of update_status
                twitter_response = client.create_tweet(text=text)

                # Safely get the data from the response
                response_data = getattr(twitter_response, 'data', None)
                if response_data:
                    post_id = response_data['id']
                else:
                    # Fallback for unexpected response format
                    current_app.logger.warning("Unexpected response format from Twitter API")
                    post_id = str(datetime.utcnow().timestamp())  # Use timestamp as fallback ID

                # Record the post in our database
                post = Post()
                post.user_id = current_user.id
                post.twitter_id = post_id
                post.text = text
                post.status = 'posted'
                post.posted_at = datetime.utcnow()
                db.session.add(post)

                # Track API usage
                QuotaTracker.track_api_call(current_user, "post")

                db.session.commit()

                flash('Post posted successfully!', 'success')
                return redirect(url_for('posts.index'))

            except tweepy.TweepyException as e:
                current_app.logger.error(f"Twitter API error: {str(e)}")
                flash(f'Error posting post: {str(e)}', 'error')
                return render_template('posts/compose.html',
                                      text=text,
                                      premium=is_premium_user,
                                      char_limit=char_limit)
            except Exception as e:
                current_app.logger.error(f"Unexpected error: {str(e)}")
                flash('An unexpected error occurred.', 'error')
                return render_template('posts/compose.html',
                                      text=text,
                                      premium=is_premium_user,
                                      char_limit=char_limit)

    # Get quota information for the user
    quota_status = QuotaTracker.get_quota_status(current_user)

    # Check if user has X Premium/Blue (verified) to determine character limit
    is_premium_user = current_user.is_verified or current_user.verified_type in ['Business', 'Government', 'Blue']
    char_limit = 4000 if is_premium_user else 280

    return render_template('posts/compose.html',
                          quota=quota_status,
                          text='',
                          premium=is_premium_user,
                          char_limit=char_limit)

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    """Delete a post."""
    post = Post.query.get_or_404(post_id)

    # Check if the post belongs to the current user
    if post.user_id != current_user.id:
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('posts.index'))

    try:
        # If the post has been posted to Twitter, delete it there too
        if post.status == 'posted' and post.twitter_id:
            try:
                # Use v2 Client instead of v1.1 API
                client = tweepy.Client(
                    consumer_key=current_user.consumer_key,
                    consumer_secret=current_user.consumer_secret,
                    access_token=current_user.access_token,
                    access_token_secret=current_user.access_token_secret
                )

                # Use delete_post method from v2 API
                client.delete_tweet(post.twitter_id)

                # Track API usage (deletion counts as an API call)
                QuotaTracker.track_api_call(current_user, "post")
            except Exception as twitter_error:
                current_app.logger.error(f"Twitter API error: {str(twitter_error)}")
                flash(f'Warning: Post deleted from database but could not be removed from X: {str(twitter_error)}', 'warning')
                # Continue to delete from our database even if Twitter API fails

        # Delete from our database
        db.session.delete(post)
        db.session.commit()

        flash('Post deleted successfully.', 'success')
    except Exception as e:
        flash('An unexpected error occurred.', 'error')
        current_app.logger.error(f"Unexpected error: {str(e)}")

    return redirect(url_for('posts.index'))

@posts_bp.route('/scheduled')
@login_required
def scheduled():
    """List scheduled posts."""
    scheduled_posts = Post.query.filter_by(
        user_id=current_user.id,
        status='scheduled'
    ).order_by(Post.scheduled_at.asc()).all()

    # Get quota information for the user
    quota_status = QuotaTracker.get_quota_status(current_user)
    return render_template('posts/scheduled.html', posts=scheduled_posts, quota=quota_status)
