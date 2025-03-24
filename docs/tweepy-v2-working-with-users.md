# Working with Users in Tweepy for Twitter API v2

This guide covers how to work with user data using Tweepy and the Twitter API v2, focusing on the capabilities available with the Free 𝕏 API Plan.

## Retrieving User Information

### Get a Single User

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get user by ID
user_by_id = client.get_user(
    id="12345678901234567890",  # Replace with actual user ID
    user_fields=["description", "created_at", "profile_image_url", "public_metrics", "verified"]
)

# Get user by username
user_by_username = client.get_user(
    username="TwitterDev",
    user_fields=["description", "created_at", "profile_image_url", "public_metrics", "verified"]
)

# Print user information
user = user_by_username.data
print(f"User: {user.name} (@{user.username})")
print(f"ID: {user.id}")
print(f"Bio: {user.description}")
print(f"Created: {user.created_at}")
print(f"Profile Image: {user.profile_image_url}")
print(f"Verified: {user.verified}")

# Print metrics
metrics = user.public_metrics
print(f"Followers: {metrics['followers_count']}")
print(f"Following: {metrics['following_count']}")
print(f"Tweets: {metrics['tweet_count']}")
print(f"Listed: {metrics['listed_count']}")
```

### Get Multiple Users

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get multiple users by ID
users_by_id = client.get_users(
    ids=["12345678901234567890", "09876543210987654321"],
    user_fields=["description", "public_metrics", "verified"]
)

# Get multiple users by username
users_by_username = client.get_users(
    usernames=["TwitterDev", "Twitter"],
    user_fields=["description", "public_metrics", "verified"]
)

# Print information for each user
for user in users_by_username.data:
    print(f"User: {user.name} (@{user.username})")
    print(f"Followers: {user.public_metrics['followers_count']}")
    print(f"Verified: {user.verified}")
    print(f"Bio: {user.description}")
    print("---")
```

### Get Authenticated User (Me)

```python
import tweepy

# User context authentication required
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Get information about the authenticated user
me = client.get_me(user_fields=["description", "public_metrics", "verified"])

user = me.data
print(f"Authenticated as: {user.name} (@{user.username})")
print(f"Bio: {user.description}")
print(f"Followers: {user.public_metrics['followers_count']}")
print(f"Following: {user.public_metrics['following_count']}")
print(f"Tweets: {user.public_metrics['tweet_count']}")
```

## Managing User Relationships

### Follow a User

```python
import tweepy

# User context authentication required
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Follow a user by their ID
response = client.follow_user("12345678901234567890")  # Replace with actual user ID

if response.data["following"]:
    print("Successfully followed user")
else:
    print("Failed to follow user")
```

### Unfollow a User

```python
import tweepy

# User context authentication required
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Unfollow a user by their ID
response = client.unfollow_user("12345678901234567890")  # Replace with actual user ID

if response.data["following"] is False:
    print("Successfully unfollowed user")
else:
    print("Failed to unfollow user")
```

### Get Followers

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get a user's followers
followers = client.get_users_followers(
    id="12345678901234567890",  # Replace with actual user ID
    max_results=10,
    user_fields=["profile_image_url", "description", "verified"]
)

print("Followers:")
for user in followers.data:
    verified = "✓" if user.verified else ""
    print(f"- {user.name} (@{user.username}) {verified}")
    if hasattr(user, "description"):
        print(f"  Bio: {user.description}")
    print()

# For paginating through all followers
print("Paginating through all followers:")
for response in tweepy.Paginator(
    client.get_users_followers, 
    id="12345678901234567890",
    max_results=100,
    limit=5  # Limit to 5 pages (500 followers)
):
    for user in response.data:
        print(f"- {user.name} (@{user.username})")
```

### Get Following

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get users that a user is following
following = client.get_users_following(
    id="12345678901234567890",  # Replace with actual user ID
    max_results=10,
    user_fields=["profile_image_url", "description", "verified"]
)

print("Following:")
for user in following.data:
    verified = "✓" if user.verified else ""
    print(f"- {user.name} (@{user.username}) {verified}")
    if hasattr(user, "description"):
        print(f"  Bio: {user.description}")
    print()
```

## Managing Blocks and Mutes

### Block Operations

```python
import tweepy

# User context authentication required
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

user_id = "12345678901234567890"  # Replace with actual user ID

# Block a user
client.block(user_id)
print("User blocked")

# Unblock a user
client.unblock(user_id)
print("User unblocked")

# Get list of blocked users
blocked = client.get_blocked(
    max_results=10,
    user_fields=["profile_image_url", "description"]
)

print("Blocked users:")
for user in blocked.data:
    print(f"- {user.name} (@{user.username})")
```

### Mute Operations

```python
import tweepy

# User context authentication required
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

user_id = "12345678901234567890"  # Replace with actual user ID

# Mute a user
client.mute(user_id)
print("User muted")

# Unmute a user
client.unmute(user_id)
print("User unmuted")

# Get list of muted users
muted = client.get_muted(
    max_results=10,
    user_fields=["profile_image_url", "description"]
)

print("Muted users:")
for user in muted.data:
    print(f"- {user.name} (@{user.username})")
```

## Getting User's Tweets

### Get User's Timeline

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get a user's most recent tweets
tweets = client.get_users_tweets(
    id="12345678901234567890",  # Replace with actual user ID
    max_results=10,
    tweet_fields=["created_at", "public_metrics"],
    exclude=["retweets", "replies"]  # Exclude retweets and replies
)

print(f"Recent tweets:")
for tweet in tweets.data:
    print(f"[{tweet.created_at}] {tweet.text}")
    print(f"Likes: {tweet.public_metrics['like_count']} | Retweets: {tweet.public_metrics['retweet_count']}")
    print("---")
```

### Get User's Mentions

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get tweets mentioning a user
mentions = client.get_users_mentions(
    id="12345678901234567890",  # Replace with actual user ID
    max_results=10,
    tweet_fields=["created_at", "author_id"],
    expansions=["author_id"],
    user_fields=["username"]
)

print(f"Recent mentions:")
for tweet in mentions.data:
    # Find the author
    author = next((user for user in mentions.includes["users"] if user.id == tweet.author_id), None)
    username = author.username if author else "unknown"
    
    print(f"@{username}: {tweet.text}")
    print(f"Date: {tweet.created_at}")
    print("---")
```

## Advanced User Queries

### Search for Users by Username

Note: The Twitter API v2 does not provide a direct endpoint for user search. For finding users by username, you'll need to use the `get_user` method with exact usernames.

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Try to find users with exact usernames
usernames = ["TwitterDev", "Twitter", "TwitterAPI"]
users = client.get_users(
    usernames=usernames,
    user_fields=["description", "public_metrics", "verified"]
)

# Check which users were found
found_usernames = [user.username for user in users.data]
for username in usernames:
    if username in found_usernames:
        print(f"✓ Found: @{username}")
    else:
        print(f"✗ Not found: @{username}")
```

## Working with User Fields

The Twitter API v2 allows you to request specific fields for user data. Here's a list of the most useful fields:

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Request all available user fields
user = client.get_user(
    username="TwitterDev",
    user_fields=[
        "created_at",           # When the account was created
        "description",          # User's bio
        "entities",             # URLs, hashtags, mentions in the bio
        "id",                   # The user's ID
        "location",             # User's location
        "name",                 # Display name
        "pinned_tweet_id",      # ID of pinned tweet
        "profile_image_url",    # Profile image
        "protected",            # Whether tweets are protected
        "public_metrics",       # Follower/following counts etc.
        "url",                  # URL in user's profile
        "username",             # @handle
        "verified",             # Whether user is verified
        "verified_type",        # Type of verification
        "withheld"              # Content withholding information
    ]
)

# Print detailed user information
user_data = user.data
print(f"User: {user_data.name} (@{user_data.username})")
print(f"Created at: {user_data.created_at}")
print(f"Bio: {user_data.description}")
print(f"Location: {user_data.location if hasattr(user_data, 'location') else 'Not specified'}")
print(f"URL: {user_data.url if hasattr(user_data, 'url') else 'Not specified'}")
print(f"Profile image: {user_data.profile_image_url}")
print(f"Protected: {user_data.protected}")
print(f"Verified: {user_data.verified}")

if hasattr(user_data, 'verified_type'):
    print(f"Verification type: {user_data.verified_type}")

print("\nMetrics:")
metrics = user_data.public_metrics
print(f"- Followers: {metrics['followers_count']}")
print(f"- Following: {metrics['following_count']}")
print(f"- Tweets: {metrics['tweet_count']}")
print(f"- Listed: {metrics['listed_count']}")

if hasattr(user_data, 'pinned_tweet_id'):
    print(f"\nPinned tweet ID: {user_data.pinned_tweet_id}")
```

## Tips and Best Practices

1. **Efficient querying**
   - Use batch methods like `get_users()` instead of multiple `get_user()` calls
   - Only request the user fields you need

2. **Rate limit awareness**
   - User endpoints have rate limits (typically 300-900 requests per 15 minutes)
   - Implement exponential backoff for rate limit errors

3. **Handling pagination**
   - Use Tweepy's Paginator for followers/following lists
   - Store pagination tokens if you need to resume later

4. **Error handling**
   - Account for protected accounts and other access restrictions
   - Handle cases where users might not exist or have been suspended