# 𝕏-Pilot

A frontend interface for managing 𝕏 (𝕏) accounts within the limitations of the Free 𝕏 API tier, powered by Tweepy.

## Features

- Authentication management for 𝕏 API
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
- 𝕏 Developer account with API credentials
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/TheSethRose/X-Pilot.git
   cd X-Pilot
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

4. Create a `.env` file with your 𝕏 API credentials:
   ```
   SECRET_KEY=your_flask_secret_key
   CONSUMER_KEY=your_api_key
   CONSUMER_SECRET=your_api_secret
   ACCESS_TOKEN=your_access_token
   ACCESS_TOKEN_SECRET=your_access_token_secret
   DATABASE_URL=sqlite:///twikit.db
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Start the application:
   ```bash
   flask run
   ```

## Project Structure

```
X-Pilot/
├── app/                  # Application code
│   ├── __init__.py       # Application factory
│   ├── models.py         # Database models
│   └── routes/           # Route blueprints
├── static/               # Static assets
│   ├── css/              # CSS files
│   └── js/               # JavaScript files
├── templates/            # HTML templates
│   ├── auth/             # Authentication templates
│   ├── errors/           # Error page templates
│   └── tweets/           # Tweet management templates
├── utils/                # Utility scripts
├── .env                  # Environment variables (create this)
├── README.md             # Project documentation
└── requirements.txt      # Project dependencies
```

## License

[MIT](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [Tweepy](https://www.tweepy.org/) - 𝕏 API library for Python
- [Flask](https://flask.palletsprojects.com/) - Web framework
