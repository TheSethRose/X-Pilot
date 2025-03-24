import os
import sys
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

def initialize_database():
    """
    Initialize the SQLite database with the required tables.
    """
    db_path = os.getenv('DATABASE_URL', 'sqlite:///twikit.db').replace('sqlite:///', '')

    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)

    print(f"Initializing database at {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        twitter_id TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        name TEXT NOT NULL,
        profile_image_url TEXT,
        consumer_key TEXT NOT NULL,
        consumer_secret TEXT NOT NULL,
        access_token TEXT NOT NULL,
        access_token_secret TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')

    # Create posts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        twitter_id TEXT UNIQUE,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scheduled_at TIMESTAMP,
        posted_at TIMESTAMP,
        status TEXT DEFAULT 'draft',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create streams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS streams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        rules TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_run TIMESTAMP,
        active BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create stream_results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stream_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id INTEGER NOT NULL,
        post_id TEXT NOT NULL,
        post_text TEXT NOT NULL,
        author_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stream_id) REFERENCES streams (id)
    )
    ''')

    # Create quota_usage table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quota_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        posts_used INTEGER DEFAULT 0,
        reset_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, month, year)
    )
    ''')

    conn.commit()
    conn.close()

    print("Database initialized successfully")

if __name__ == "__main__":
    initialize_database()
