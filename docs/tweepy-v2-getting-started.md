# Getting Started with Tweepy and 𝕏 API v2

This guide provides a quick introduction to using Tweepy with the 𝕏 (𝕏) API v2, focusing specifically on the Free API tier. It covers the essential steps to get your application up and running.

## Prerequisites

Before you begin, you'll need:

1. Python 3.7 or later
2. A 𝕏 Developer account
3. An approved developer app with API credentials

## Installation

Install Tweepy using pip:

```bash
pip install tweepy
```

For async support, use:

```bash
pip install "tweepy[async]"
```

## Setting Up Developer Access

1. Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new Project and App
3. Generate the necessary credentials:
   - API Key and API Secret
   - Bearer Token (for app-only authentication)
   - Access Token and Access Token Secret (for user context)

## Basic Authentication

### App-Only Authentication (OAuth 2.0 Bearer Token)

This is the simplest authentication method for read-only access:

```python
import tweepy

# Initialize the client with your bearer token
client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Test the connection
me = client.get_user(username="TwitterDev")
print(f"User ID: {me.data.id}")
print(f"Username: {me.data.username}")
```

### User Context Authentication (OAuth 1.0a)

For actions that require user context:

```python
import tweepy

# Initialize with OAuth 1.0a credentials
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Test posting a post (requires user context)
response = client.create_post(text="Hello, 𝕏 API v2!")
print(f"Post posted with ID: {response.data['id']}")
```

## Basic Operations

### Reading Posts

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get a single post
post = client.get_post(
    "1234567890",  # Replace with actual post ID
    post_fields=["created_at", "author_id", "public_metrics"]
)

print(f"Post text: {post.data.text}")
print(f"Created at: {post.data.created_at}")
print(f"Like count: {post.data.public_metrics['like_count']}")
```

### Searching for Posts

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Search for recent posts (limited to 7 days with free tier)
search_results = client.search_recent_posts(
    query="python tweepy",
    max_results=10,
    post_fields=["created_at", "author_id"]
)

for post in search_results.data:
    print(f"Post ID: {post.id}")
    print(f"Content: {post.text}")
    print(f"Created at: {post.created_at}")
    print("---")
```

### Getting User Information

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get user by username
user = client.get_user(
    username="TwitterDev",
    user_fields=["description", "public_metrics", "verified"]
)

print(f"User ID: {user.data.id}")
print(f"Username: {user.data.username}")
print(f"Description: {user.data.description}")
print(f"Followers: {user.data.public_metrics['followers_count']}")
print(f"Verified: {user.data.verified}")
```

## Next Steps

For more advanced usage and complete API reference, refer to:

1. [Comprehensive Tweepy V2 API Overview](@docs/tweepy-v2-api-overview.md)
2. [Official Tweepy Documentation](https://docs.tweepy.org/)
3. [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
