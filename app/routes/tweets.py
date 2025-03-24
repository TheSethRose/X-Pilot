from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
import tweepy
from datetime import datetime

from app.models import db, Tweet
from utils.quota_tracker import QuotaTracker

tweets_bp = Blueprint('tweets', __name__, url_prefix='/tweets')

@tweets_bp.route('/')
@login_required
def index():
    """List user's tweets."""
    tweets = Tweet.query.filter_by(user_id=current_user.id).order_by(Tweet.created_at.desc()).all()
    # Get quota information for the user
    quota_status = QuotaTracker.get_quota_status(current_user)
    return render_template('tweets/index.html', tweets=tweets, quota=quota_status)

@tweets_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    """Compose and post a new tweet."""
    if request.method == 'POST':
        text = request.form.get('text', '').strip()

        if not text:
            flash('Tweet content cannot be empty.', 'error')
            return render_template('tweets/compose.html', text='')

        # Check if user has X Premium/Blue (verified) to determine character limit
        # X Premium/Blue users can post up to 4000/10000 characters depending on their tier
        # Regular users are limited to 280 characters
        is_premium_user = current_user.is_verified or current_user.verified_type in ['Business', 'Government', 'Blue']
        char_limit = 4000 if is_premium_user else 280

        if len(text) > char_limit:
            flash(f'Tweet exceeds {char_limit} character limit for your account type.', 'error')
            return render_template('tweets/compose.html', text=text, premium=is_premium_user, char_limit=char_limit)

        # Check if scheduling is requested
        schedule_checkbox = request.form.get('schedule')
        schedule_date = request.form.get('schedule_date')
        schedule_time = request.form.get('schedule_time')

        if schedule_checkbox and schedule_date and schedule_time:
            # Create a scheduled tweet
            try:
                scheduled_at = datetime.strptime(f"{schedule_date} {schedule_time}", "%Y-%m-%d %H:%M")

                if scheduled_at <= datetime.utcnow():
                    flash('Scheduled time must be in the future.', 'error')
                    return render_template('tweets/compose.html',
                                          text=text,
                                          premium=is_premium_user,
                                          char_limit=char_limit)

                # Create a scheduled tweet
                tweet = Tweet()
                tweet.user_id = current_user.id
                tweet.text = text
                tweet.status = 'scheduled'
                tweet.scheduled_at = scheduled_at
                db.session.add(tweet)
                db.session.commit()

                flash('Tweet scheduled successfully!', 'success')
                return redirect(url_for('tweets.scheduled'))

            except ValueError:
                flash('Invalid date or time format.', 'error')
                return render_template('tweets/compose.html',
                                      text=text,
                                      premium=is_premium_user,
                                      char_limit=char_limit)
        else:
            # Post tweet immediately
            try:
                # Check quota before posting
                quota_status = QuotaTracker.get_quota_status(current_user)

                if quota_status['posts_used'] >= quota_status['monthly_limit']:
                    flash('API quota limit reached. Cannot post tweet.', 'error')
                    return render_template('tweets/compose.html',
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

                # Use create_tweet method from v2 API instead of update_status
                twitter_response = client.create_tweet(text=text)

                # Safely get the data from the response
                response_data = getattr(twitter_response, 'data', None)
                if response_data:
                    tweet_id = response_data['id']
                else:
                    # Fallback for unexpected response format
                    current_app.logger.warning("Unexpected response format from Twitter API")
                    tweet_id = str(datetime.utcnow().timestamp())  # Use timestamp as fallback ID

                # Record the tweet in our database
                tweet = Tweet()
                tweet.user_id = current_user.id
                tweet.twitter_id = tweet_id
                tweet.text = text
                tweet.status = 'posted'
                tweet.posted_at = datetime.utcnow()
                db.session.add(tweet)

                # Track API usage
                QuotaTracker.track_api_call(current_user, "post")

                db.session.commit()

                flash('Tweet posted successfully!', 'success')
                return redirect(url_for('tweets.index'))

            except tweepy.TweepyException as e:
                current_app.logger.error(f"Twitter API error: {str(e)}")
                flash(f'Error posting tweet: {str(e)}', 'error')
                return render_template('tweets/compose.html',
                                      text=text,
                                      premium=is_premium_user,
                                      char_limit=char_limit)
            except Exception as e:
                current_app.logger.error(f"Unexpected error: {str(e)}")
                flash('An unexpected error occurred.', 'error')
                return render_template('tweets/compose.html',
                                      text=text,
                                      premium=is_premium_user,
                                      char_limit=char_limit)

    # Get quota information for the user
    quota_status = QuotaTracker.get_quota_status(current_user)

    # Check if user has X Premium/Blue (verified) to determine character limit
    is_premium_user = current_user.is_verified or current_user.verified_type in ['Business', 'Government', 'Blue']
    char_limit = 4000 if is_premium_user else 280

    return render_template('tweets/compose.html',
                          quota=quota_status,
                          text='',
                          premium=is_premium_user,
                          char_limit=char_limit)

@tweets_bp.route('/<int:tweet_id>/delete', methods=['POST'])
@login_required
def delete(tweet_id):
    """Delete a tweet."""
    tweet = Tweet.query.get_or_404(tweet_id)

    # Check if the tweet belongs to the current user
    if tweet.user_id != current_user.id:
        flash('You do not have permission to delete this tweet.', 'danger')
        return redirect(url_for('tweets.index'))

    try:
        # If the tweet has been posted to Twitter, delete it there too
        if tweet.status == 'posted' and tweet.twitter_id:
            try:
                # Use v2 Client instead of v1.1 API
                client = tweepy.Client(
                    consumer_key=current_user.consumer_key,
                    consumer_secret=current_user.consumer_secret,
                    access_token=current_user.access_token,
                    access_token_secret=current_user.access_token_secret
                )

                # Use delete_tweet method from v2 API
                client.delete_tweet(tweet.twitter_id)

                # Track API usage (deletion counts as an API call)
                QuotaTracker.track_api_call(current_user, "post")
            except Exception as twitter_error:
                current_app.logger.error(f"Twitter API error: {str(twitter_error)}")
                flash(f'Warning: Tweet deleted from database but could not be removed from X: {str(twitter_error)}', 'warning')
                # Continue to delete from our database even if Twitter API fails

        # Delete from our database
        db.session.delete(tweet)
        db.session.commit()

        flash('Tweet deleted successfully.', 'success')
    except Exception as e:
        flash('An unexpected error occurred.', 'error')
        current_app.logger.error(f"Unexpected error: {str(e)}")

    return redirect(url_for('tweets.index'))

@tweets_bp.route('/scheduled')
@login_required
def scheduled():
    """List scheduled tweets."""
    scheduled_tweets = Tweet.query.filter_by(
        user_id=current_user.id,
        status='scheduled'
    ).order_by(Tweet.scheduled_at.asc()).all()

    # Get quota information for the user
    quota_status = QuotaTracker.get_quota_status(current_user)
    return render_template('tweets/scheduled.html', tweets=scheduled_tweets, quota=quota_status)
