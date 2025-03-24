# Tweepy for 𝕏 (𝕏) API v2: Comprehensive Overview

This document provides a comprehensive overview of Tweepy's capabilities for interacting with 𝕏 (𝕏) API v2, focusing specifically on what's available with the Free 𝕏 API Plan.

## Table of Contents

- [Introduction](#introduction)
- [Authentication](#authentication)
- [Client vs AsyncClient](#client-vs-asyncclient)
- [Available API Features](#available-api-features)
  - [Posts](#posts)
  - [Users](#users)
  - [Spaces](#spaces)
  - [Lists](#lists)
  - [Direct Messages](#direct-messages)
  - [Streaming](#streaming)
- [Working with Expansions and Fields](#working-with-expansions-and-fields)
- [Pagination](#pagination)
- [Rate Limits](#rate-limits)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Code Examples](#code-examples)

## Introduction

Twitter's API v2 is the current version of the 𝕏 API, and it's accessible through Tweepy's `Client` and `AsyncClient` classes. As of April 2023, the 𝕏 API v1.1 is no longer accessible with Essential (free) access, meaning all free tier developers must use the v2 API.

Tweepy provides a Pythonic interface to the 𝕏 API v2, making it easier to interact with Twitter's endpoints while handling authentication, rate limiting, and pagination.

## Authentication

Twitter API v2 requires authentication to access its endpoints. For the Free 𝕏 API Plan, you'll need to create a developer account and get API credentials.

### Setting Up Authentication

1. Create a developer account at [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a project and app to generate API credentials
3. Get your API Key, API Key Secret, and Bearer Token

### Authentication Methods

Tweepy supports multiple authentication methods for the 𝕏 API v2:

1. **OAuth 2.0 Bearer Token (App-Only)** - Simplest method for read-only access:
   ```python
   import tweepy
   client = tweepy.Client("YOUR_BEARER_TOKEN")
   ```

2. **OAuth 1.0a User Context** - For actions on behalf of a user:
   ```python
   import tweepy
   client = tweepy.Client(
       consumer_key="API_KEY",
       consumer_secret="API_KEY_SECRET",
       access_token="ACCESS_TOKEN",
       access_token_secret="ACCESS_TOKEN_SECRET"
   )
   ```

3. **OAuth 2.0 Authorization Code Flow with PKCE** - For user context with OAuth 2.0:
   ```python
   import tweepy

   # Set up OAuth 2.0 handler
   oauth2_user_handler = tweepy.OAuth2UserHandler(
       client_id="CLIENT_ID",
       redirect_uri="CALLBACK_URL",
       scope=["post.read", "users.read", "offline.access"],
   )

   # Get authorization URL
   auth_url = oauth2_user_handler.get_authorization_url()

   # After user authorizes, get the tokens from the callback
   response = oauth2_user_handler.fetch_token("AUTHORIZATION_RESPONSE_URL")
   access_token = response["access_token"]

   # Use the access token
   client = tweepy.Client(access_token)
   ```

## Client vs AsyncClient

Tweepy provides two main client classes for interacting with the 𝕏 API v2:

1. **Client** - Synchronous client for regular Python code
2. **AsyncClient** - Asynchronous client for use with `async`/`await` pattern

Both clients provide the same functionality, but `AsyncClient` is designed for asynchronous applications using Python's asyncio.

## Available API Features

The Free 𝕏 API Plan provides access to a subset of 𝕏 API v2 endpoints. Here's what you can access:

### Posts

#### Reading Posts

- **Lookup Posts by ID**:
  ```python
  client.get_post(id)
  client.get_posts([id1, id2, ...])
  ```

- **Search Recent Posts** (Limited to 7 days of data):
  ```python
  client.search_recent_posts(query)
  ```

- **Get User Timeline**:
  ```python
  client.get_users_posts(user_id)
  ```

- **Get User Mentions**:
  ```python
  client.get_users_mentions(user_id)
  ```

- **Get Post Counts** (Volume of matching posts):
  ```python
  client.get_recent_posts_count(query)
  ```

#### Engage with Posts

- **Like a Post**:
  ```python
  client.like(post_id)
  ```

- **Unlike a Post**:
  ```python
  client.unlike(post_id)
  ```

- **Repost**:
  ```python
  client.repost(post_id)
  ```

- **Remove Repost**:
  ```python
  client.unrepost(post_id)
  ```

- **Bookmark a Post**:
  ```python
  client.bookmark(post_id)
  ```

- **Remove Bookmark**:
  ```python
  client.remove_bookmark(post_id)
  ```

- **Hide/Unhide Replies**:
  ```python
  client.hide_reply(post_id)
  client.unhide_reply(post_id)
  ```

#### Managing Posts

- **Create a Post**:
  ```python
  client.create_post(text="Hello, World!")
  ```

- **Delete a Post**:
  ```python
  client.delete_post(post_id)
  ```

#### Additional Post Information

- **Get Liking Users**:
  ```python
  client.get_liking_users(post_id)
  ```

- **Get Reposters**:
  ```python
  client.get_reposters(post_id)
  ```

- **Get Quote Posts**:
  ```python
  client.get_quote_posts(post_id)
  ```

### Users

#### User Information

- **Lookup User by ID or Username**:
  ```python
  client.get_user(id=user_id)
  client.get_user(username="username")
  ```

- **Lookup Multiple Users**:
  ```python
  client.get_users(ids=[id1, id2, ...])
  client.get_users(usernames=["user1", "user2", ...])
  ```

- **Get Authenticated User**:
  ```python
  client.get_me()
  ```

#### User Relationships

- **Follow a User**:
  ```python
  client.follow_user(target_user_id)
  ```

- **Unfollow a User**:
  ```python
  client.unfollow_user(target_user_id)
  ```

- **Get Followers**:
  ```python
  client.get_users_followers(user_id)
  ```

- **Get Following**:
  ```python
  client.get_users_following(user_id)
  ```

- **Block, Unblock, and View Blocks**:
  ```python
  client.block(target_user_id)
  client.unblock(target_user_id)
  client.get_blocked()
  ```

- **Mute, Unmute, and View Mutes**:
  ```python
  client.mute(target_user_id)
  client.unmute(target_user_id)
  client.get_muted()
  ```

### Spaces

#### Spaces Information

- **Lookup Space**:
  ```python
  client.get_space(id)
  ```

- **Lookup Multiple Spaces**:
  ```python
  client.get_spaces(ids=[id1, id2, ...])
  ```

- **Search Spaces**:
  ```python
  client.search_spaces(query)
  ```

- **Get Space Posts**:
  ```python
  client.get_space_posts(space_id)
  ```

### Lists

#### List Management

- **Create a List**:
  ```python
  client.create_list(name, description)
  ```

- **Update a List**:
  ```python
  client.update_list(id, name, description)
  ```

- **Delete a List**:
  ```python
  client.delete_list(id)
  ```

#### List Members

- **Add User to List**:
  ```python
  client.add_list_member(list_id, user_id)
  ```

- **Remove User from List**:
  ```python
  client.remove_list_member(list_id, user_id)
  ```

- **Get List Members**:
  ```python
  client.get_list_members(list_id)
  ```

#### List Information

- **Get User's Lists**:
  ```python
  client.get_owned_lists(user_id)
  ```

- **Get List Posts**:
  ```python
  client.get_list_posts(list_id)
  ```

### Direct Messages

Direct Messages have limited functionality on the Free 𝕏 API Plan.

- **Create Direct Message**:
  ```python
  client.create_direct_message(participant_id, text)
  ```

- **Get Direct Messages**:
  ```python
  client.get_direct_message_events()
  ```

### Streaming

The filtered stream allows you to receive Posts in real-time that match your specified rules.

```python
import tweepy

class MyStreamingClient(tweepy.StreamingClient):
    def on_post(self, post):
        print(post.text)

# Initialize with your bearer token
streaming_client = MyStreamingClient("YOUR_BEARER_TOKEN")

# Add rules
streaming_client.add_rules(tweepy.StreamRule("python"))

# Start streaming
streaming_client.filter()
```

## Working with Expansions and Fields

Twitter API v2 uses a concept of expansions and fields to control what data is returned in responses.

### Expansions

Expansions allow you to request additional related objects. For example, when getting a Post, you can expand user information:

```python
client.get_post(
    id,
    expansions=["author_id", "referenced_posts.id", "attachments.media_keys"]
)
```

### Fields

Fields allow you to specify which attributes to include for each object type:

```python
client.get_post(
    id,
    post_fields=["created_at", "public_metrics", "source"],
    user_fields=["profile_image_url", "verified", "description"],
    media_fields=["preview_image_url", "type", "url"]
)
```

## Pagination

Tweepy provides a `Paginator` class to handle pagination for endpoints that return multiple items:

```python
# Get all posts from a user's timeline
for post in tweepy.Paginator(client.get_users_posts, user_id, max_results=100).flatten(limit=200):
    print(post.id, post.text)
```

The `flatten()` method consolidates all pages into a single iterator of items.

To access `includes` data, you need to iterate through each response instead:

```python
for response in tweepy.Paginator(client.get_users_posts, user_id, max_results=100, user_fields=["description"]):
    for user in response.includes.get("users", []):
        print(user.id, user.description)
```

## Rate Limits

All 𝕏 API v2 endpoints have rate limits. The Free 𝕏 API Plan has stricter limits compared to paid tiers:

- Most read operations: 500-1500 requests per 15-minute window
- Most write operations: 25-50 requests per 15-minute window
- Search endpoints: 60-450 requests per 15-minute window
- Some endpoints (like search_all_posts) are limited to 1 request per second

When you exceed a rate limit, the API returns a 429 error. Tweepy will raise a `TooManyRequests` exception.

## Common Issues and Solutions

### Not Getting Expansions or Fields Data

When printing objects directly, you might only see default fields. The data is still accessible as attributes:

```python
post = client.get_post(id, expansions=["author_id"], user_fields=["description"])
print(post.includes["users"][0].description)  # Access the description
```

### Rate Limiting with search_all_posts

The `search_all_posts` endpoint has an additional 1 request per second rate limit:

```python
import time
for response in tweepy.Paginator(client.search_all_posts, query):
    # Process response
    time.sleep(1)  # Add 1 second delay between requests
```

## Code Examples

### Basic Post Lookup

```python
import tweepy

# Authentication
client = tweepy.Client("YOUR_BEARER_TOKEN")

# Get a single post with expansions
post = client.get_post(
    id="1234567890",
    expansions=["author_id", "attachments.media_keys"],
    post_fields=["created_at", "public_metrics"],
    user_fields=["profile_image_url", "verified"]
)

# Print post data
print(f"Post: {post.data.text}")
print(f"Created at: {post.data.created_at}")
print(f"Likes: {post.data.public_metrics['like_count']}")

# Access author information from includes
if "users" in post.includes:
    author = post.includes["users"][0]
    print(f"Author: {author.username}")
    print(f"Verified: {author.verified}")
```

### Search Recent Posts

```python
import tweepy

# Authentication
client = tweepy.Client("YOUR_BEARER_TOKEN")

# Search for recent posts
search_results = client.search_recent_posts(
    query="python",
    max_results=10,
    post_fields=["created_at", "public_metrics"],
    expansions=["author_id"],
    user_fields=["profile_image_url"]
)

# Process results
for post in search_results.data:
    print(f"Post by @{next((user.username for user in search_results.includes['users'] if user.id == post.author_id), 'unknown')}: {post.text}")
```

### Post a Post

```python
import tweepy

# Authentication with OAuth 1.0a
client = tweepy.Client(
    consumer_key="API_KEY",
    consumer_secret="API_KEY_SECRET",
    access_token="ACCESS_TOKEN",
    access_token_secret="ACCESS_TOKEN_SECRET"
)

# Post a post
response = client.create_post(text="Hello, 𝕏 API v2 with Tweepy!")
print(f"Post posted with ID: {response.data['id']}")
```

### Stream Posts in Real-time

```python
import tweepy

# Create a streaming client subclass
class PostPrinter(tweepy.StreamingClient):
    def on_post(self, post):
        print(f"Post ID: {post.id}")
        print(f"Text: {post.text}")
        print("---")

# Authenticate and initialize the streaming client
streaming_client = PostPrinter("YOUR_BEARER_TOKEN")

# Delete existing rules if needed
existing_rules = streaming_client.get_rules()
if existing_rules.data:
    rule_ids = [rule.id for rule in existing_rules.data]
    streaming_client.delete_rules(rule_ids)

# Add new filter rules
streaming_client.add_rules(tweepy.StreamRule("python"))
streaming_client.add_rules(tweepy.StreamRule("tweepy"))

# Start the stream
streaming_client.filter(
    post_fields=["created_at", "author_id"],
    expansions=["author_id"],
    user_fields=["username"]
)
```

---

This overview covers the main capabilities of Tweepy when working with 𝕏 API v2 on the Free 𝕏 API Plan. For more detailed information, refer to the [official Tweepy documentation](https://docs.tweepy.org/) and the [Twitter API v2 documentation](https://developer.twitter.com/en/docs/twitter-api).
