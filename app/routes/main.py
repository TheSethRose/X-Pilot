from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.models import Tweet
from utils.quota_tracker import QuotaTracker

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

    # Get quota information
    quota_status = QuotaTracker.get_quota_status(current_user)

    # Get tweet counts and recent activity
    tweets = Tweet.query.filter_by(user_id=current_user.id).order_by(Tweet.created_at.desc()).all()
    tweet_count = len(tweets)
    recent_tweets = tweets[:5]  # Get 5 most recent tweets

    # Get count of scheduled tweets
    scheduled_count = Tweet.query.filter_by(
        user_id=current_user.id,
        status='scheduled'
    ).count()

    # For now, we can't get follower counts without additional API calls
    # We'll update this later when implementing profile management
    follower_count = "N/A"
    following_count = "N/A"

    return render_template(
        'main/dashboard.html',
        quota_percentage=quota_status['percentage'],
        quota_used=quota_status['posts_used'],
        quota_reset_date=quota_status['reset_date'],
        tweet_count=tweet_count,
        recent_tweets=recent_tweets,
        scheduled_count=scheduled_count,
        follower_count=follower_count,
        following_count=following_count
    )
