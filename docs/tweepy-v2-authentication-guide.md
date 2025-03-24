# Tweepy Authentication Guide for 𝕏 API v2

This guide covers the authentication methods available for the 𝕏 API v2 using Tweepy, with a focus on the Free 𝕏 API Plan.

## Available Authentication Methods

Twitter API v2 supports several authentication methods, each with different capabilities:

1. **OAuth 2.0 Bearer Token (App-Only)** - For read-only access to public data
2. **OAuth 1.0a User Context** - For actions on behalf of a user
3. **OAuth 2.0 Authorization Code Flow with PKCE** - Modern OAuth for user context

## OAuth 2.0 Bearer Token (App-Only)

This is the simplest method to authenticate with the 𝕏 API v2. It provides read-only access to public information.

### Step 1: Get Your Bearer Token

1. Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Navigate to your Project and App
3. In the "Keys and tokens" tab, generate or view your Bearer Token

### Step 2: Initialize the Client

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Test the connection
user = client.get_user(username="TwitterDev")
print(f"User: {user.data.name} (@{user.data.username})")
```

### Capabilities

With Bearer Token authentication, you can:
- Read public posts
- Search for posts
- Get user information
- Retrieve followers and following lists
- Access public lists

You cannot perform write operations like posting posts or sending DMs.

## OAuth 1.0a User Context

This method allows your application to perform actions on behalf of a user, including write operations.

### Step 1: Get Your API Keys and Access Tokens

1. Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Navigate to your Project and App
3. In the "Keys and tokens" tab:
   - Get your API Key and Secret (Consumer Keys)
   - Generate Access Token and Secret for your account

### Step 2: Initialize the Client

```python
import tweepy

client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

# Test by posting a post
response = client.create_post(text="Testing 𝕏 API v2 with OAuth 1.0a!")
print(f"Post posted with ID: {response.data['id']}")
```

### Capabilities

With OAuth 1.0a authentication, you can:
- Perform all read operations
- Post posts
- Delete posts
- Like, repost, and bookmark posts
- Follow and unfollow users
- Create and manage lists
- Send direct messages

## OAuth 2.0 Authorization Code Flow with PKCE

This is the modern approach for obtaining user context access, providing enhanced security.

### Step 1: Configure Your App for OAuth 2.0

1. Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Navigate to your Project and App settings
3. Configure the OAuth 2.0 settings:
   - Add a Callback URL / Redirect URI
   - Set the App permissions (read, write, etc.)
   - Select the appropriate OAuth 2.0 scopes

### Step 2: Implement the Authorization Flow

```python
import tweepy

# Initialize the OAuth 2.0 handler
oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id="YOUR_CLIENT_ID",
    redirect_uri="YOUR_CALLBACK_URL",
    scope=["post.read", "post.write", "users.read", "follows.read", "follows.write"],
    # The scope determines what your app can access
)

# Get the authorization URL to redirect the user
print(f"Authorization URL: {oauth2_user_handler.get_authorization_url()}")

# After user authorizes, they'll be redirected to your callback URL with a code
# Get this code from the URL and use it to fetch tokens
authorization_response = input("Enter the full callback URL: ")
tokens = oauth2_user_handler.fetch_token(authorization_response)

# Get the access token
access_token = tokens["access_token"]

# Initialize the client with the access token
client = tweepy.Client(access_token)

# Test the connection
me = client.get_me()
print(f"Authenticated as: {me.data.name} (@{me.data.username})")
```

### Capabilities

OAuth 2.0 provides similar capabilities to OAuth 1.0a but with:
- More granular permissions through scopes
- Better security with PKCE
- Standardized token refresh mechanisms

## Best Practices

1. **Keep credentials secure**
   - Never hardcode tokens in your application
   - Use environment variables or secure storage
   - For production, consider using a secrets manager

2. **Use the right authentication method**
   - Bearer Token for simple read-only applications
   - OAuth 1.0a or 2.0 for user context operations

3. **Handle token expiration**
   - Bearer Tokens generally don't expire
   - OAuth 2.0 access tokens expire - implement refresh token handling

4. **Scope management**
   - Only request the scopes you need
   - More limited scopes improve security and user trust

## Troubleshooting

### 401 Unauthorized

- Verify your tokens are correct and not expired
- Ensure you're using the correct authentication method for the endpoint
- Check that your App has the necessary permissions configured

### 403 Forbidden

- Your authentication is valid, but you don't have permission for that action
- Verify your App has the correct access level
- Check that the requested operation is available on the Free 𝕏 API Plan

## References

- [Tweepy Documentation](https://docs.tweepy.org/)
- [Twitter API v2 Authentication Documentation](https://developer.twitter.com/en/docs/authentication/overview)
- [Twitter OAuth 2.0 Documentation](https://developer.twitter.com/en/docs/authentication/oauth-2-0)
