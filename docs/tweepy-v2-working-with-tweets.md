# Working with Posts in Tweepy for 𝕏 API v2

This guide covers how to work with posts using Tweepy and the 𝕏 API v2, focusing on the capabilities available with the Free 𝕏 API Plan.

## Reading Posts

### Getting a Single Post

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get a single post by ID
post = client.get_post(
    id="1234567890",  # Replace with actual post ID
    post_fields=["created_at", "author_id", "public_metrics", "source"],
    user_fields=["name", "username", "profile_image_url"],
    expansions=["author_id"]
)

# Access basic post information
print(f"Post text: {post.data.text}")
print(f"Created at: {post.data.created_at}")
print(f"Post ID: {post.data.id}")

# Access metrics
metrics = post.data.public_metrics
print(f"Likes: {metrics['like_count']}")
print(f"Reposts: {metrics['repost_count']}")
print(f"Replies: {metrics['reply_count']}")
print(f"Quote Posts: {metrics['quote_count']}")

# Access author information from expansions
if "users" in post.includes:
    author = post.includes["users"][0]
    print(f"Author: {author.name} (@{author.username})")
    print(f"Profile image: {author.profile_image_url}")
```

### Getting Multiple Posts

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get multiple posts by ID
posts = client.get_posts(
    ids=["1234567890", "9876543210"],  # Replace with actual post IDs
    post_fields=["created_at", "public_metrics"],
    expansions=["author_id"],
    user_fields=["username"]
)

# Process each post
for post in posts.data:
    print(f"Post ID: {post.id}")
    print(f"Text: {post.text}")
    print(f"Created at: {post.created_at}")
    print(f"Likes: {post.public_metrics['like_count']}")
    print("---")

# Access author information using post.author_id
for post in posts.data:
    author = next((user for user in posts.includes["users"] if user.id == post.author_id), None)
    if author:
        print(f"Post by @{author.username}: {post.text}")
```

### Searching for Posts

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Search for recent posts (limited to 7 days with free tier)
search_results = client.search_recent_posts(
    query="python tweepy",
    max_results=10,
    post_fields=["created_at", "public_metrics"],
    expansions=["author_id"],
    user_fields=["username", "verified"]
)

# Process search results
if not search_results.data:
    print("No posts found matching the query")
else:
    for post in search_results.data:
        # Find the author for this post
        author = next((user for user in search_results.includes["users"] if user.id == post.author_id), None)
        username = author.username if author else "unknown"
        verified = "✓" if author and author.verified else ""

        print(f"@{username} {verified}: {post.text}")
        print(f"Likes: {post.public_metrics['like_count']} | Reposts: {post.public_metrics['repost_count']}")
        print(f"Created at: {post.created_at}")
        print("---")
```

## Creating and Managing Posts

### Posting a Post

```python
import tweepy

# User context authentication required for posting
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Post a simple post
response = client.create_post(text="Hello, 𝕏 API v2!")
print(f"Post posted with ID: {response.data['id']}")

# Post a post with a poll
response = client.create_post(
    text="What's your favorite programming language?",
    poll_options=["Python", "JavaScript", "Java", "Other"],
    poll_duration_minutes=1440  # 24 hours
)
print(f"Poll posted with ID: {response.data['id']}")

# Reply to a post
response = client.create_post(
    text="This is a reply!",
    in_reply_to_post_id="1234567890"  # Replace with actual post ID
)
print(f"Reply posted with ID: {response.data['id']}")

# Quote post
response = client.create_post(
    text="Check out this interesting post!",
    quote_post_id="1234567890"  # Replace with actual post ID
)
print(f"Quote posted with ID: {response.data['id']}")
```

### Deleting a Post

```python
import tweepy

# User context authentication required for deleting
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Delete a post
response = client.delete_post("1234567890")  # Replace with actual post ID

if response.data["deleted"]:
    print("Post successfully deleted")
else:
    print("Failed to delete post")
```

## Engaging with Posts

### Like, Unlike, Repost, and Unrepost

```python
import tweepy

# User context authentication required for engagement
client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

post_id = "1234567890"  # Replace with actual post ID

# Like a post
client.like(post_id)
print("Post liked")

# Unlike a post
client.unlike(post_id)
print("Post unliked")

# Repost
client.repost(post_id)
print("Post reposted")

# Undo repost
client.unrepost(post_id)
print("Repost removed")
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

post_id = "1234567890"  # Replace with actual post ID

# Bookmark a post
client.bookmark(post_id)
print("Post bookmarked")

# Remove bookmark
client.remove_bookmark(post_id)
print("Bookmark removed")

# Hide a reply
client.hide_reply(post_id)
print("Reply hidden")

# Unhide a reply
client.unhide_reply(post_id)
print("Reply unhidden")
```

## Getting Post Interactions

### Who Liked a Post

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get users who liked a post
liking_users = client.get_liking_users(
    id="1234567890",  # Replace with actual post ID
    user_fields=["profile_image_url", "description", "public_metrics"]
)

print(f"Users who liked this post:")
for user in liking_users.data:
    followers = user.public_metrics["followers_count"]
    print(f"- @{user.username} ({user.name}) - {followers} followers")
    if hasattr(user, "description"):
        print(f"  Bio: {user.description}")
    print()
```

### Who Reposted a Post

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get users who reposted a post
reposters = client.get_reposters(
    id="1234567890",  # Replace with actual post ID
    user_fields=["profile_image_url", "verified"]
)

print(f"Users who reposted this post:")
for user in reposters.data:
    verified = "✓" if user.verified else ""
    print(f"- @{user.username} {verified}")
```

### Get Quote Posts

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Get quote posts
quotes = client.get_quote_posts(
    id="1234567890",  # Replace with actual post ID
    max_results=10,
    expansions=["author_id"],
    user_fields=["username"]
)

print(f"Quote posts:")
for quote in quotes.data:
    # Find the author
    author = next((user for user in quotes.includes["users"] if user.id == quote.author_id), None)
    username = author.username if author else "unknown"

    print(f"@{username}: {quote.text}")
    print("---")
```

## Working with Media

Note: For media uploads with the 𝕏 API v2, you need to use the v1.1 media upload endpoint and then reference the media ID in your v2 post creation.

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

# Post post with media using v2 API
response = client.create_post(
    text="Check out this image!",
    media_ids=[media_id]
)
print(f"Post with media posted: {response.data['id']}")
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
