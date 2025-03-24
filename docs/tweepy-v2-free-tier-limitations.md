# 𝕏 (𝕏) API Free Tier Limitations with Tweepy

This guide outlines the specific limitations of the 𝕏 (𝕏) API Free Tier and how they apply when using Tweepy. Understanding these limitations is crucial for developing applications that comply with Twitter's terms of service.

## Official Free Tier Limitations

According to [Twitter's official documentation](https://docs.x.com/x-api/getting-started/about-x-api), the Free Tier has the following limitations:

- **Purpose**: For write-only use cases and testing the X API
- **Rate Limits**: Low rate-limit access to v2 posts and media upload endpoints
- **Post Cap**: 1,500 Posts per month (posting limit at the app level)
- **Project Limits**: 1 Project, 1 App per Project, 1 Environment
- **Additional Access**: Login with X, Access to Ads API
- **Cost**: Free

## Tweepy Functionality Under Free Tier

When using Tweepy with the Free Tier, you're limited to the following capabilities:

### Available Write Operations

```python
# Post a post
client.create_post(text="Hello, world!")

# Post with media (using v1.1 API for upload)
auth = tweepy.OAuth1UserHandler("CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")
api = tweepy.API(auth)  # v1.1 API for media upload
media = api.media_upload("image.jpg")
client.create_post(text="Post with media", media_ids=[media.media_id])

# Delete a post
client.delete_post(post_id)

# Reply to a post
client.create_post(text="This is a reply", in_reply_to_post_id="1234567890")
```

### Testing API Operations

The Free Tier is designed primarily for testing and limited post creation. This means you can:

1. Test authentication flows
2. Test posting functionality
3. Validate your app's integration with Twitter

### Limited Read Access

With the Free Tier, you have limited access to read operations. You can:

```python
# Get your own user information
me = client.get_me()

# Very limited access to user lookups
user = client.get_user(username="username")
```

## What You Cannot Do with Free Tier

Understanding what's not included is equally important:

1. **No Search Access**: You cannot search for posts or users
2. **No Timeline Access**: You cannot retrieve user timelines
3. **No Filtered Stream**: You cannot access the streaming API
4. **No Post Pulls**: You cannot retrieve posts from other users beyond very limited operations
5. **Limited Rate Limits**: Very restricted number of API calls per timeframe

## Monthly Post Cap Management

The 1,500 posts per month limit applies at the app level. This means:

- All users of your app share this allocation
- There's no way to increase this limit without upgrading to a paid tier
- You should implement tracking to monitor your usage

```python
# Example of how you might track post usage
import datetime
import sqlite3

def log_post_creation(post_id, user_id):
    conn = sqlite3.connect('post_log.db')
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS post_log
                 (id INTEGER PRIMARY KEY, post_id TEXT, user_id TEXT,
                  created_at TIMESTAMP)''')

    # Insert a row
    c.execute("INSERT INTO post_log VALUES (NULL, ?, ?, ?)",
              (post_id, user_id, datetime.datetime.now()))

    # Get count for current month
    first_day = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    c.execute("SELECT COUNT(*) FROM post_log WHERE created_at >= ?", (first_day,))
    count = c.fetchone()[0]

    conn.commit()
    conn.close()

    return count, 1500 - count  # Return current count and remaining

# After posting a post
response = client.create_post(text="Hello, world!")
post_id = response.data['id']
count, remaining = log_post_creation(post_id, "user123")
print(f"Posted post. Monthly usage: {count}/1500. Remaining: {remaining}")
```

## Best Practices for Free Tier

1. **Focus on Write Operations**: Since the Free Tier is primarily for posting, optimize your app for creating content rather than consuming it.

2. **Implement Usage Tracking**: Monitor your monthly post usage to avoid hitting the 1,500 limit unexpectedly.

3. **Test Efficiently**: Use test accounts and minimize unnecessary API calls during development.

4. **Consider Upgrade Paths**: If your application needs read access or more posting capacity, plan for upgrading to Basic or Pro tiers.

5. **Leverage Other Authentications**: The Free Tier includes "Login with X" functionality, which can be used for authentication purposes even if you don't need extensive API access.

## Comparison with Paid Tiers

| Feature | Free | Basic ($100/month) | Pro ($5000/month) |
|---------|------|-------------------|-------------------|
| Post creation | 1,500/month | 3,000/month | 300,000/month |
| Post reading | ❌ | 10,000/month | 1,000,000/month |
| Projects | 1 | 1 | 1 |
| Apps per project | 1 | 2 | 3 |
| Filtered stream | ❌ | ❌ | ✓ |
| Full-archive search | ❌ | ❌ | ✓ |

## Use Cases Compatible with Free Tier

Based on the [Twitter API documentation](https://docs.x.com/x-api/what-to-build), these are use cases that can work with the Free Tier's limitations:

1. **Simple Bots**: Create bots that post scheduled or event-triggered content
2. **Post Automation**: Schedule and automate posting for individual accounts
3. **Cross-Platform Publishing**: Post to 𝕏 as part of a multi-platform publishing solution
4. **Testing Integrations**: Test 𝕏 integration before upgrading to a paid tier
5. **Login with X**: Authenticate users in your app using their 𝕏 accounts

## Conclusion

The Free Tier of Twitter's API is primarily designed for testing and limited write operations. While it provides a way to get started with the 𝕏 API, its limitations make it unsuitable for applications that require reading posts, searching, or accessing user timelines at scale.

For development purposes, the Free Tier is sufficient to test authentication and basic posting functionality. However, for production applications that require more functionality, consider upgrading to the Basic or Pro tiers.
