"""
Twitter OAuth utilities for authentication with Twitter API.
"""
import tweepy
from flask import current_app, url_for, session, redirect
from urllib.parse import urlencode
import os
import requests

class TwitterOAuth:
    """Handler for Twitter OAuth 1.0a authentication."""

    @staticmethod
    def is_simulation_enabled():
        """Check if simulation mode is enabled."""
        sim_value = os.getenv('SIMULATE_OAUTH', 'false').lower()
        return sim_value == 'true' or sim_value == '1' or sim_value == 'yes'

    @staticmethod
    def get_oauth_handler(callback_url=None):
        """Create and return an OAuthHandler instance."""
        # For simulated mode, return None if that's enabled
        if TwitterOAuth.is_simulation_enabled():
            current_app.logger.debug("Skipping OAuth handler creation in simulation mode")
            return None

        consumer_key = current_app.config['TWITTER_CONSUMER_KEY']
        consumer_secret = current_app.config['TWITTER_CONSUMER_SECRET']

        current_app.logger.debug(f"Creating OAuth handler with key: {consumer_key[:4]}... and callback: {callback_url}")

        if not consumer_key or not consumer_secret:
            current_app.logger.error("Missing Twitter API credentials in configuration")
            return None

        try:
            auth = tweepy.OAuth1UserHandler(
                consumer_key,
                consumer_secret,
                callback=callback_url
            )
            return auth
        except Exception as e:
            current_app.logger.error(f"Error creating OAuth handler: {e}")
            return None

    @staticmethod
    def get_authorization_url(callback_url=None):
        """Get the authorization URL for Twitter OAuth."""
        if not callback_url:
            callback_url = url_for('auth.twitter_callback', _external=True)
            current_app.logger.debug(f"Generated callback URL: {callback_url}")

        # For local testing with full simulation
        if TwitterOAuth.is_simulation_enabled():
            current_app.logger.warning("Using simulated OAuth flow for local testing")
            # Directly redirect to our callback with a fake verifier
            # This avoids any redirects to Twitter
            fake_callback = f"{callback_url}?oauth_verifier=fake_verifier"
            current_app.logger.debug(f"Created simulated callback URL: {fake_callback}")
            return fake_callback

        # Normal OAuth flow
        auth = TwitterOAuth.get_oauth_handler(callback_url)

        if not auth:
            current_app.logger.error("Failed to create OAuth handler")
            return None

        try:
            current_app.logger.debug("Attempting to get authorization URL from Twitter")
            redirect_url = auth.get_authorization_url()
            # Store the request token for later use in the callback
            session['request_token'] = auth.request_token
            current_app.logger.debug(f"Authorization URL obtained: {redirect_url[:30]}...")
            return redirect_url
        except tweepy.TweepyException as e:
            current_app.logger.error(f"Error getting authorization URL: {e}")
            # Try using API v1.1 auth URL directly
            current_app.logger.info("Trying fallback to direct OAuth URL")
            try:
                # Direct OAuth URL construction (for testing)
                oauth_url = "https://api.twitter.com/oauth/authorize"
                params = {"oauth_callback": callback_url}
                return f"{oauth_url}?{urlencode(params)}"
            except Exception as e2:
                current_app.logger.error(f"Error with fallback auth URL: {e2}")
                return None

    @staticmethod
    def get_access_token(oauth_verifier):
        """Get access token from the oauth_verifier received from Twitter."""
        # For local testing with full simulation
        if TwitterOAuth.is_simulation_enabled():
            current_app.logger.warning("Using simulated OAuth tokens for local testing")
            return {
                'access_token': os.getenv('ACCESS_TOKEN'),
                'access_token_secret': os.getenv('ACCESS_TOKEN_SECRET')
            }

        request_token = session.get('request_token')

        if not request_token:
            current_app.logger.error("No request token found in session")
            return None

        current_app.logger.debug(f"Using request token to get access token")
        auth = TwitterOAuth.get_oauth_handler()

        if not auth:
            current_app.logger.error("Failed to create OAuth handler for access token")
            return None

        auth.request_token = request_token

        try:
            auth.get_access_token(oauth_verifier)
            current_app.logger.debug("Successfully obtained access token")
            return {
                'access_token': auth.access_token,
                'access_token_secret': auth.access_token_secret
            }
        except tweepy.TweepyException as e:
            current_app.logger.error(f"Error getting access token: {e}")
            return None

    @staticmethod
    def get_api_client(access_token=None, access_token_secret=None):
        """Create a Tweepy API client instance."""
        # For local testing with full simulation, return a mock api
        if TwitterOAuth.is_simulation_enabled():
            current_app.logger.warning("Using simulated API client for local testing")
            # Return None and handle this in get_user_info
            return None

        consumer_key = current_app.config['TWITTER_CONSUMER_KEY']
        consumer_secret = current_app.config['TWITTER_CONSUMER_SECRET']

        # If tokens not provided, try to get from current_app config (if available)
        if not access_token:
            access_token = current_app.config.get('TWITTER_ACCESS_TOKEN')
        if not access_token_secret:
            access_token_secret = current_app.config.get('TWITTER_ACCESS_TOKEN_SECRET')

        if not access_token or not access_token_secret:
            current_app.logger.error("No access tokens available")
            return None

        current_app.logger.debug(f"Creating API client with consumer key: {consumer_key[:4]}...")
        try:
            auth = tweepy.OAuth1UserHandler(
                consumer_key,
                consumer_secret,
                access_token,
                access_token_secret
            )
            return tweepy.API(auth)
        except Exception as e:
            current_app.logger.error(f"Error creating API client: {e}")
            return None

    @staticmethod
    def get_user_info(access_token, access_token_secret):
        """Get user info from Twitter API."""
        # For local testing, simulate a successful response immediately
        if TwitterOAuth.is_simulation_enabled():
            current_app.logger.warning("Using simulated user info for local testing")
            return {
                'twitter_id': '12345678',
                'username': 'test_user',
                'name': 'Test User',
                'profile_image_url': 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png',
            }

        api = TwitterOAuth.get_api_client(access_token, access_token_secret)

        if not api:
            current_app.logger.error("Failed to create API client")
            return None

        try:
            current_app.logger.debug("Verifying credentials with Twitter API")
            user_info = api.verify_credentials(include_email=True)
            current_app.logger.debug(f"Got user info for: {user_info.screen_name}")
            return {
                'twitter_id': user_info.id_str,
                'username': user_info.screen_name,
                'name': user_info.name,
                'profile_image_url': user_info.profile_image_url_https,
            }
        except tweepy.TweepyException as e:
            current_app.logger.error(f"Error getting user info: {e}")
            return None
