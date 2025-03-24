# Streaming with Tweepy for Twitter API v2

This guide covers how to use the streaming capabilities of Tweepy with the Twitter API v2, focusing on what's available with the Free 𝕏 API Plan.

## Introduction to Twitter API v2 Streaming

Twitter API v2 offers filtered stream access, which allows you to receive tweets in real-time that match specific rules you define. Tweepy provides a convenient interface for working with these streams through the `StreamingClient` class.

With the Free 𝕏 API Plan, you can:
- Connect to the filtered stream endpoint
- Define rules to filter the stream
- Receive tweets matching your rules in real-time

## Basic Streaming Setup

### Creating a StreamingClient

To work with the streaming API, you'll need to create a subclass of `tweepy.StreamingClient` and define handlers for the events you want to process:

```python
import tweepy

class MyStreamingClient(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        """Called when a tweet is received"""
        print(f"Tweet ID: {tweet.id}")
        print(f"Text: {tweet.text}")
        print(f"Author ID: {tweet.author_id}")
        print("---")
    
    def on_includes(self, includes):
        """Called when includes data is received"""
        if "users" in includes:
            for user in includes["users"]:
                print(f"User: {user.username}")
    
    def on_errors(self, errors):
        """Called when errors are received"""
        for error in errors:
            print(f"Error: {error}")
    
    def on_connect(self):
        """Called when the connection is established"""
        print("Stream connected")
    
    def on_disconnect(self):
        """Called when the connection is lost"""
        print("Stream disconnected")
    
    def on_connection_error(self):
        """Called when a connection error occurs"""
        print("Connection error")
    
    def on_request_error(self, status_code, response):
        """Called when a request error occurs"""
        print(f"Request error: {status_code}")
        print(response)

# Initialize with your bearer token
streaming_client = MyStreamingClient("YOUR_BEARER_TOKEN")
```

## Managing Stream Rules

Before starting a stream, you'll need to define rules that specify which tweets to receive. Rules are persistent and will stay active even when your connection is closed.

### Adding Rules

```python
import tweepy

# Initialize the client
streaming_client = tweepy.StreamingClient("YOUR_BEARER_TOKEN")

# Add a simple keyword rule
streaming_client.add_rules(tweepy.StreamRule("python"))

# Add a rule with multiple keywords
streaming_client.add_rules(tweepy.StreamRule("python tweepy"))

# Add a rule with a tag (for identifying which rule matched)
streaming_client.add_rules(tweepy.StreamRule("machine learning", tag="ML"))

# Add multiple rules at once
rules = [
    tweepy.StreamRule("python", tag="python"),
    tweepy.StreamRule("javascript", tag="js"),
    tweepy.StreamRule("from:TwitterDev", tag="twitter-dev")
]
streaming_client.add_rules(rules)
```

### Viewing Existing Rules

```python
import tweepy

streaming_client = tweepy.StreamingClient("YOUR_BEARER_TOKEN")

# Get all current rules
rules = streaming_client.get_rules()

print("Current stream rules:")
if not rules.data:
    print("No rules found")
else:
    for rule in rules.data:
        print(f"ID: {rule.id}")
        print(f"Value: {rule.value}")
        if rule.tag:
            print(f"Tag: {rule.tag}")
        print("---")
```

### Deleting Rules

```python
import tweepy

streaming_client = tweepy.StreamingClient("YOUR_BEARER_TOKEN")

# Delete a specific rule by ID
streaming_client.delete_rules("1234567890")  # Replace with actual rule ID

# Delete multiple rules by ID
streaming_client.delete_rules(["1234567890", "0987654321"])

# Delete all existing rules
existing_rules = streaming_client.get_rules()
if existing_rules.data:
    rule_ids = [rule.id for rule in existing_rules.data]
    streaming_client.delete_rules(rule_ids)
    print("All rules deleted")
else:
    print("No rules to delete")
```

## Starting the Stream

### Basic Stream

```python
import tweepy

class MyStreamingClient(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(f"{tweet.id}: {tweet.text}")

# Initialize the client
streaming_client = MyStreamingClient("YOUR_BEARER_TOKEN")

# Make sure we have a rule defined
if not streaming_client.get_rules().data:
    streaming_client.add_rules(tweepy.StreamRule("python"))

# Start the stream
streaming_client.filter()
```

### Stream with Additional Tweet Fields

```python
import tweepy

class MyStreamingClient(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(f"Tweet by {tweet.author_id}: {tweet.text}")
        if hasattr(tweet, "created_at"):
            print(f"Created at: {tweet.created_at}")
        if hasattr(tweet, "public_metrics"):
            metrics = tweet.public_metrics
            print(f"Likes: {metrics['like_count']} | Retweets: {metrics['retweet_count']}")
        print("---")

# Initialize the client
streaming_client = MyStreamingClient("YOUR_BEARER_TOKEN")

# Add rules if needed
if not streaming_client.get_rules().data:
    streaming_client.add_rules(tweepy.StreamRule("python"))

# Start the stream with additional tweet fields
streaming_client.filter(
    tweet_fields=["created_at", "public_metrics", "source"],
    expansions=["author_id"],
    user_fields=["username", "verified"]
)
```

### Stream with Expansions and Matching Rules

```python
import tweepy

class MyStreamingClient(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(f"Tweet: {tweet.text}")
    
    def on_includes(self, includes):
        if "users" in includes:
            for user in includes["users"]:
                print(f"User: @{user.username}")
    
    def on_matching_rules(self, matching_rules):
        for rule in matching_rules:
            print(f"Matched rule: {rule.tag if rule.tag else rule.id}")

# Initialize the client
streaming_client = MyStreamingClient("YOUR_BEARER_TOKEN")

# Add rules with tags
streaming_client.delete_rules([rule.id for rule in streaming_client.get_rules().data or []])
streaming_client.add_rules([
    tweepy.StreamRule("python", tag="python"),
    tweepy.StreamRule("tweepy", tag="tweepy-lib")
])

# Start the stream with expansions and matching rules
streaming_client.filter(
    expansions=["author_id"],
    user_fields=["username", "verified"]
)
```

## Advanced Streaming Techniques

### Running the Stream in a Background Thread

```python
import tweepy
import threading

class MyStreamingClient(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(f"Tweet received: {tweet.text}")
    
    def on_exception(self, exception):
        print(f"Error: {exception}")
        return True  # Don't stop the stream on exception

# Initialize the client
streaming_client = MyStreamingClient("YOUR_BEARER_TOKEN")

# Make sure we have rules
if not streaming_client.get_rules().data:
    streaming_client.add_rules(tweepy.StreamRule("python"))

# Start the stream in a background thread
stream_thread = threading.Thread(target=streaming_client.filter)
stream_thread.daemon = True  # Thread will close when main program exits
stream_thread.start()

print("Stream started in background thread")
print("Main program continues execution...")

# To disconnect the stream later
# streaming_client.disconnect()
```

### Handling Reconnection

```python
import tweepy
import time

class MyStreamingClient(tweepy.StreamingClient):
    def __init__(self, bearer_token, max_retries=3, retry_delay=5):
        super().__init__(bearer_token)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retries = 0
    
    def on_tweet(self, tweet):
        print(f"Tweet: {tweet.text}")
    
    def on_connection_error(self):
        if self.retries < self.max_retries:
            self.retries += 1
            print(f"Connection error. Retry {self.retries} of {self.max_retries} in {self.retry_delay} seconds...")
            time.sleep(self.retry_delay)
            # Exponential backoff
            self.retry_delay *= 2
        else:
            print("Maximum retries reached. Stopping stream.")
            return False  # Stop retrying
        return True  # Continue retrying
    
    def on_connect(self):
        print("Connected to stream")
        self.retries = 0
        self.retry_delay = 5  # Reset retry delay

# Initialize and start the streaming client
streaming_client = MyStreamingClient("YOUR_BEARER_TOKEN")

# Add rules if needed
if not streaming_client.get_rules().data:
    streaming_client.add_rules(tweepy.StreamRule("python"))

# Start the stream
streaming_client.filter()
```

### Processing Tweets with Queue

```python
import tweepy
import threading
import queue
import time

# Create a queue for tweet processing
tweet_queue = queue.Queue()

class MyStreamingClient(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        # Instead of processing here, add to queue
        tweet_queue.put(tweet)

# Function to process tweets from the queue
def process_tweets():
    while True:
        try:
            # Get a tweet from the queue
            tweet = tweet_queue.get(timeout=60)
            
            # Process the tweet
            print(f"Processing tweet: {tweet.id}")
            print(f"Text: {tweet.text}")
            
            # Simulate processing time
            time.sleep(0.5)
            
            # Mark the task as done
            tweet_queue.task_done()
            
        except queue.Empty:
            print("No tweets received for 60 seconds")
            continue
        except Exception as e:
            print(f"Error processing tweet: {e}")
            continue

# Initialize the streaming client
streaming_client = MyStreamingClient("YOUR_BEARER_TOKEN")

# Make sure we have rules
if not streaming_client.get_rules().data:
    streaming_client.add_rules(tweepy.StreamRule("python"))

# Start the tweet processing thread
processing_thread = threading.Thread(target=process_tweets)
processing_thread.daemon = True
processing_thread.start()

# Start the stream
streaming_client.filter()
```

## Stream Rules Syntax

Twitter API v2 streams use a powerful rule syntax for filtering tweets. Here are some examples:

### Basic Operators

```python
import tweepy

streaming_client = tweepy.StreamingClient("YOUR_BEARER_TOKEN")

# Clear existing rules
existing_rules = streaming_client.get_rules()
if existing_rules.data:
    streaming_client.delete_rules([rule.id for rule in existing_rules.data])

# Add rules with different operators
rules = [
    # Keyword matching
    tweepy.StreamRule("python", tag="python-keyword"),
    
    # Multiple keywords (OR)
    tweepy.StreamRule("python OR javascript", tag="languages"),
    
    # All keywords (AND)
    tweepy.StreamRule("python javascript", tag="both-languages"),
    
    # Exact phrase
    tweepy.StreamRule('"machine learning"', tag="exact-phrase"),
    
    # Exclude keyword
    tweepy.StreamRule("python -django", tag="python-not-django"),
    
    # From a specific user
    tweepy.StreamRule("from:TwitterDev", tag="twitter-dev"),
    
    # To a specific user
    tweepy.StreamRule("to:TwitterDev", tag="to-twitter-dev"),
    
    # Tweets containing a URL
    tweepy.StreamRule("url:github", tag="github-links"),
    
    # Tweets with hashtag
    tweepy.StreamRule("#python", tag="python-hashtag"),
    
    # Tweets with media
    tweepy.StreamRule("has:media python", tag="python-with-media"),
    
    # Retweets
    tweepy.StreamRule("is:retweet python", tag="python-retweets"),
    
    # Complex combination
    tweepy.StreamRule('python (flask OR django) -"web scraping" has:links', tag="python-web-frameworks-with-links")
]

# Add all rules
streaming_client.add_rules(rules)

# Display added rules
current_rules = streaming_client.get_rules()
for rule in current_rules.data:
    print(f"Rule {rule.id} (Tag: {rule.tag}): {rule.value}")
```

## Tips and Best Practices

1. **Rule Management**
   - Keep track of your rule IDs and tags
   - Limit the number of rules (Free tier has a lower limit)
   - Use specific rules to reduce noise

2. **Error Handling**
   - Implement reconnection logic for network issues
   - Handle exceptions in all event methods

3. **Performance**
   - Use background threads for processing
   - Consider using a queue for high-volume streams

4. **Resource Management**
   - Disconnect streams when not in use
   - Be aware of connection timeouts

5. **Rate Limiting**
   - The streaming API has connection limits
   - Implement exponential backoff for reconnection attempts