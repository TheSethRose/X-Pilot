# 𝕏Pilot

A frontend interface for managing Twitter (𝕏) accounts within the limitations of the Free Twitter API tier, powered by Tweepy.

## Features

- Authentication management for Twitter API
- Tweet posting, deletion, and scheduling
- User relationship management (follow/unfollow, block/mute)
- User information and metrics viewing
- Tweet engagement (like, retweet, bookmark)
- List management
- Streaming capabilities
- Basic analytics
- Automated actions

## Getting Started

### Prerequisites

- Python 3.7 or later
- Twitter Developer account with API credentials
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/xpilot.git
   cd xpilot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Twitter API credentials:
   ```
   CONSUMER_KEY=your_api_key
   CONSUMER_SECRET=your_api_secret
   ACCESS_TOKEN=your_access_token
   ACCESS_TOKEN_SECRET=your_access_token_secret
   ```

5. Initialize the database:
   ```bash
   python utils/init_db.py
   ```

6. Start the application:
   ```bash
   flask run
   ```

## License

[MIT](LICENSE)
