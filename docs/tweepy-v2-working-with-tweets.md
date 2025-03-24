# Working with Tweets in Tweepy for 𝕏 API v2

This guide covers how to work with tweets using Tweepy and the 𝕏 API v2, focusing on the capabilities available with the Free 𝕏 API Plan.

## Reading Tweets

### Getting a Single Tweet

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get a single tweet by ID
tweet = client.get_tweet(
    id="1234567890",  # Replace with actual tweet ID
    tweet_fields=["created_at", "author_id", "public_metrics", "source"],
    user_fields=["name", "username", "profile_image_url"],
    expansions=["author_id"]
)

# Access basic tweet information
print(f"Tweet text: {tweet.data.text}")
print(f"Created at: {tweet.data.created_at}")
print(f"Tweet ID: {tweet.data.id}")

# Access metrics
metrics = tweet.data.public_metrics
print(f"Likes: {metrics['like_count']}")
print(f"Retweets: {metrics['retweet_count']}")
print(f"Replies: {metrics['reply_count']}")
print(f"Quote Tweets: {metrics['quote_count']}")

# Access author information from expansions
if "users" in tweet.includes:
    author = tweet.includes["users"][0]
    print(f"Author: {author.name} (@{author.username})")
    print(f"Profile image: {author.profile_image_url}")
```

### Getting Multiple Tweets

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get multiple tweets by ID
tweets = client.get_tweets(
    ids=["1234567890", "9876543210"],  # Replace with actual tweet IDs
    tweet_fields=["created_at", "public_metrics"],
    expansions=["author_id"],
    user_fields=["username"]
)

# Process each tweet
for tweet in tweets.data:
    print(f"Tweet ID: {tweet.id}")
    print(f"Text: {tweet.text}")
    print(f"Created at: {tweet.created_at}")
    print(f"Likes: {tweet.public_metrics['like_count']}")
    print("---")

# Access author information using tweet.author_id
for tweet in tweets.data:
    author = next((user for user in tweets.includes["users"] if user.id == tweet.author_id), None)
    if author:
        print(f"Tweet by @{author.username}: {tweet.text}")
```

### Searching for Tweets

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Search for recent tweets (limited to 7 days with free tier)
search_results = client.search_recent_tweets(
    query="python tweepy",
    max_results=10,
    tweet_fields=["created_at", "public_metrics"],
    expansions=["author_id"],
    user_fields=["username", "verified"]
)

# Process search results
if not search_results.data:
    print("No tweets found matching the query")
else:
    for tweet in search_results.data:
        # Find the author for this tweet
        author = next((user for user in search_results.includes["users"] if user.id == tweet.author_id), None)
        username = author.username if author else "unknown"
        verified = "✓" if author and author.verified else ""

        print(f"@{username} {verified}: {tweet.text}")
        print(f"Likes: {tweet.public_metrics['like_count']} | Retweets: {tweet.public_metrics['retweet_count']}")
        print(f"Created at: {tweet.created_at}")
        print("---")
```

## Creating and Managing Tweets

### Posting a Tweet

```python
import tweepy

# User context authentication required for posting
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Post a simple tweet
response = client.create_tweet(text="Hello, 𝕏 API v2!")
print(f"Tweet posted with ID: {response.data['id']}")

# Post a tweet with a poll
response = client.create_tweet(
    text="What's your favorite programming language?",
    poll_options=["Python", "JavaScript", "Java", "Other"],
    poll_duration_minutes=1440  # 24 hours
)
print(f"Poll tweet posted with ID: {response.data['id']}")

# Reply to a tweet
response = client.create_tweet(
    text="This is a reply!",
    in_reply_to_tweet_id="1234567890"  # Replace with actual tweet ID
)
print(f"Reply posted with ID: {response.data['id']}")

# Quote tweet
response = client.create_tweet(
    text="Check out this interesting tweet!",
    quote_tweet_id="1234567890"  # Replace with actual tweet ID
)
print(f"Quote tweet posted with ID: {response.data['id']}")
```

### Deleting a Tweet

```python
import tweepy

# User context authentication required for deleting
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Delete a tweet
response = client.delete_tweet("1234567890")  # Replace with actual tweet ID

if response.data["deleted"]:
    print("Tweet successfully deleted")
else:
    print("Failed to delete tweet")
```

## Engaging with Tweets

### Like, Unlike, Retweet, and Unretweet

```python
import tweepy

# User context authentication required for engagement
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

tweet_id = "1234567890"  # Replace with actual tweet ID

# Like a tweet
client.like(tweet_id)
print("Tweet liked")

# Unlike a tweet
client.unlike(tweet_id)
print("Tweet unliked")

# Retweet
client.retweet(tweet_id)
print("Tweet retweeted")

# Undo retweet
client.unretweet(tweet_id)
print("Retweet removed")
```

### Bookmark and Hide Replies

```python
import tweepy

# User context authentication
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

tweet_id = "1234567890"  # Replace with actual tweet ID

# Bookmark a tweet
client.bookmark(tweet_id)
print("Tweet bookmarked")

# Remove bookmark
client.remove_bookmark(tweet_id)
print("Bookmark removed")

# Hide a reply
client.hide_reply(tweet_id)
print("Reply hidden")

# Unhide a reply
client.unhide_reply(tweet_id)
print("Reply unhidden")
```

## Getting Tweet Interactions

### Who Liked a Tweet

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get users who liked a tweet
liking_users = client.get_liking_users(
    id="1234567890",  # Replace with actual tweet ID
    user_fields=["profile_image_url", "description", "public_metrics"]
)

print(f"Users who liked this tweet:")
for user in liking_users.data:
    followers = user.public_metrics["followers_count"]
    print(f"- @{user.username} ({user.name}) - {followers} followers")
    if hasattr(user, "description"):
        print(f"  Bio: {user.description}")
    print()
```

### Who Retweeted a Tweet

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get users who retweeted a tweet
retweeters = client.get_retweeters(
    id="1234567890",  # Replace with actual tweet ID
    user_fields=["profile_image_url", "verified"]
)

print(f"Users who retweeted this tweet:")
for user in retweeters.data:
    verified = "✓" if user.verified else ""
    print(f"- @{user.username} {verified}")
```

### Get Quote Tweets

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get quote tweets
quotes = client.get_quote_tweets(
    id="1234567890",  # Replace with actual tweet ID
    max_results=10,
    expansions=["author_id"],
    user_fields=["username"]
)

print(f"Quote tweets:")
for quote in quotes.data:
    # Find the author
    author = next((user for user in quotes.includes["users"] if user.id == quote.author_id), None)
    username = author.username if author else "unknown"

    print(f"@{username}: {quote.text}")
    print("---")
```

## Working with Media

Note: For media uploads with the 𝕏 API v2, you need to use the v1.1 media upload endpoint and then reference the media ID in your v2 tweet creation.

```python
import tweepy

# Initialize both v1 and v2 interfaces
auth = tweepy.OAuth1UserHandler(
    "YOUR_API_KEY", "YOUR_API_KEY_SECRET",
    "YOUR_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN_SECRET"
)
api = tweepy.API(auth)  # v1.1 API for media upload
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Upload media using v1.1 API
media = api.media_upload("image.jpg")
media_id = media.media_id

# Post tweet with media using v2 API
response = client.create_tweet(
    text="Check out this image!",
    media_ids=[media_id]
)
print(f"Tweet with media posted: {response.data['id']}")
```

## Tips and Best Practices

1. **Use fields and expansions wisely**
   - Only request the fields you need to minimize API load
   - Use expansions to get related data in a single request

2. **Handle errors gracefully**
   - Wrap API calls in try/except blocks
   - Check for rate limits and implement backoff strategies

3. **Paginate for large result sets**
   - Use tweepy.Paginator for endpoints that return multiple items
   - Implement delays between pagination requests

4. **Respect user privacy**
   - Only collect and store data in compliance with Twitter's terms
   - Obtain proper consent when necessary

5. **Monitor rate limits**
   - The Free 𝕏 API Plan has limited request quotas
   - Implement tracking to avoid hitting limits
