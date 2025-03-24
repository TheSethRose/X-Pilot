from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
import tweepy
from datetime import datetime

from app.models import db, Tweet, QuotaUsage

tweets_bp = Blueprint('tweets', __name__, url_prefix='/tweets')

@tweets_bp.route('/')
@login_required
def index():
    """List user's tweets."""
    tweets = Tweet.query.filter_by(user_id=current_user.id).order_by(Tweet.created_at.desc()).all()
    return render_template('tweets/index.html', tweets=tweets)

@tweets_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    """Compose and post a new tweet."""
    if request.method == 'POST':
        # Placeholder for tweet posting logic
        current_app.logger.info(f"User {current_user.username} is attempting to post a tweet")
        return "Tweet posting not yet implemented"

    return render_template('tweets/compose.html')

@tweets_bp.route('/<int:tweet_id>/delete', methods=['POST'])
@login_required
def delete(tweet_id):
    """Delete a tweet."""
    tweet = Tweet.query.get_or_404(tweet_id)

    # Check if the tweet belongs to the current user
    if tweet.user_id != current_user.id:
        flash('You do not have permission to delete this tweet.', 'danger')
        return redirect(url_for('tweets.index'))

    # Placeholder for tweet deletion logic
    current_app.logger.info(f"User {current_user.username} is attempting to delete tweet {tweet_id}")
    return "Tweet deletion not yet implemented"

@tweets_bp.route('/scheduled')
@login_required
def scheduled():
    """List scheduled tweets."""
    scheduled_tweets = Tweet.query.filter_by(
        user_id=current_user.id,
        status='scheduled'
    ).order_by(Tweet.scheduled_at.asc()).all()

    return render_template('tweets/scheduled.html', tweets=scheduled_tweets)
