# Tweepy for Twitter (𝕏) API v2 Documentation

Welcome to the comprehensive documentation for using Tweepy with the Twitter (𝕏) API v2. This documentation focuses specifically on the capabilities available with the Free 𝕏 API Plan.

## Documentation Guides

### Core Guides

- [Comprehensive API Overview](tweepy-v2-api-overview.md) - Complete overview of all Tweepy capabilities with Twitter API v2
- [Getting Started Guide](tweepy-v2-getting-started.md) - Quick start guide for setting up and using Tweepy
- [Free Tier Limitations](tweepy-v2-free-tier-limitations.md) - Detailed breakdown of Free API tier limitations and capabilities

### Feature-Specific Guides

- [Authentication Guide](tweepy-v2-authentication-guide.md) - Detailed information on authentication methods
- [Working with Tweets](tweepy-v2-working-with-tweets.md) - Guide for reading, creating, and interacting with tweets
- [Working with Users](tweepy-v2-working-with-users.md) - Guide for user operations and relationships
- [Streaming Guide](tweepy-v2-streaming-guide.md) - Real-time tweet streaming with filtered streams
- [Conversation Moderation](tweepy-v2-conversation-moderation.md) - Guide for moderating conversations with limited Free tier capabilities

## Available Features in the Free 𝕏 API Plan

The Free 𝕏 API Plan provides access to a limited subset of Twitter API v2 capabilities:

- **Purpose**: For write-only use cases and testing the X API
- **Rate Limits**: Low rate-limit access to v2 posts and media upload endpoints
- **Post Cap**: 1,500 Posts per month (posting limit at the app level)
- **Project Limits**: 1 Project, 1 App per Project, 1 Environment
- **Additional Access**: Login with X, Access to Ads API
- **Cost**: Free

For more details on limitations, see the [Free Tier Limitations](tweepy-v2-free-tier-limitations.md) guide.

### Authentication

- OAuth 2.0 Bearer Token (App-Only Authentication)
- OAuth 1.0a User Context
- OAuth 2.0 Authorization Code Flow with PKCE

### Tweets

- Reading tweets by ID (very limited)
- Posting and deleting tweets
- Liking, retweeting, and bookmarking (limited)
- Hiding replies

### Users

- Looking up users by ID or username (limited)
- Following and unfollowing users
- Getting followers and following lists (limited)
- Blocking and muting users

### Rate Limits

The Free 𝕏 API Plan has very restricted rate limits focused primarily on write operations.

## Getting Help

If you encounter issues or need additional help:

- [Official Tweepy Documentation](https://docs.tweepy.org/)
- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy GitHub Repository](https://github.com/tweepy/tweepy)
- [Twitter Developer Forum](https://twittercommunity.com/)

## Code Examples

Each guide includes specific code examples for the covered features. Here's a quick example to get you started:

```python
import tweepy

# Authentication
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Post a tweet
response = client.create_tweet(text="Hello, world!")
print(f"Tweet posted with ID: {response.data['id']}")
```

## Contributing

If you'd like to contribute to these docs:

1. Fork the repository
2. Make your changes
3. Submit a pull request with clear descriptions of your updates

We welcome all contributions to improve and expand this documentation!
