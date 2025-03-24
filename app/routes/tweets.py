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
            return render_template('tweets/compose.html')

        if len(text) > 280:
            flash('Tweet exceeds 280 character limit.', 'error')
            return render_template('tweets/compose.html', text=text)

        # Check if scheduling is requested
        schedule_date = request.form.get('schedule_date')
        schedule_time = request.form.get('schedule_time')

        if schedule_date and schedule_time:
            # Create a scheduled tweet
            try:
                scheduled_at = datetime.strptime(f"{schedule_date} {schedule_time}", "%Y-%m-%d %H:%M")

                if scheduled_at <= datetime.utcnow():
                    flash('Scheduled time must be in the future.', 'error')
                    return render_template('tweets/compose.html', text=text)

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
                return render_template('tweets/compose.html', text=text)
        else:
            # Post tweet immediately
            try:
                # Check quota before posting
                quota_status = QuotaTracker.get_quota_status(current_user)

                if quota_status['posts_used'] >= quota_status['limit']:
                    flash('API quota limit reached. Cannot post tweet.', 'error')
                    return render_template('tweets/compose.html', text=text, quota=quota_status)

                # Post to Twitter
                auth = tweepy.OAuth1UserHandler(
                    current_user.consumer_key,
                    current_user.consumer_secret,
                    current_user.access_token,
                    current_user.access_token_secret
                )
                api = tweepy.API(auth)
                twitter_response = api.update_status(text)

                # Record the tweet in our database
                tweet = Tweet()
                tweet.user_id = current_user.id
                tweet.twitter_id = str(twitter_response.id)
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
                return render_template('tweets/compose.html', text=text)
            except Exception as e:
                current_app.logger.error(f"Unexpected error: {str(e)}")
                flash('An unexpected error occurred.', 'error')
                return render_template('tweets/compose.html', text=text)

    # Get quota information for the user
    quota_status = QuotaTracker.get_quota_status(current_user)
    return render_template('tweets/compose.html', quota=quota_status)

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
            auth = tweepy.OAuth1UserHandler(
                current_user.consumer_key,
                current_user.consumer_secret,
                current_user.access_token,
                current_user.access_token_secret
            )
            api = tweepy.API(auth)
            api.destroy_status(tweet.twitter_id)

            # Track API usage (deletion counts as an API call)
            QuotaTracker.track_api_call(current_user, "post")

        # Delete from our database
        db.session.delete(tweet)
        db.session.commit()

        flash('Tweet deleted successfully.', 'success')
    except tweepy.TweepyException as e:
        flash(f'Error deleting tweet: {str(e)}', 'error')
        current_app.logger.error(f"Twitter API error: {str(e)}")
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
