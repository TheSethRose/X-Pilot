from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for Twitter authentication."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    twitter_id = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    profile_image_url = db.Column(db.String(256), nullable=True)

    # Authentication data
    consumer_key = db.Column(db.String(64), nullable=False)
    consumer_secret = db.Column(db.String(64), nullable=False)
    access_token = db.Column(db.String(64), nullable=False)
    access_token_secret = db.Column(db.String(64), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    tweets = db.relationship('Tweet', backref='user', lazy=True, cascade='all, delete-orphan')
    streams = db.relationship('Stream', backref='user', lazy=True, cascade='all, delete-orphan')
    quota_usage = db.relationship('QuotaUsage', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

class Tweet(db.Model):
    """Tweet model for managing tweets."""
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    twitter_id = db.Column(db.String(64), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(280), nullable=False)

    # Media attachments could be stored as JSON string
    media_attachments = db.Column(db.Text, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_at = db.Column(db.DateTime, nullable=True)
    posted_at = db.Column(db.DateTime, nullable=True)

    # Status: draft, scheduled, posted, failed
    status = db.Column(db.String(16), default='draft')

    def __repr__(self):
        return f'<Tweet {self.id}>'

    @property
    def media(self):
        """Get media attachments as a list."""
        if self.media_attachments:
            return json.loads(self.media_attachments)
        return []

    @media.setter
    def media(self, attachments):
        """Set media attachments from a list."""
        if attachments:
            self.media_attachments = json.dumps(attachments)
        else:
            self.media_attachments = None


class Stream(db.Model):
    """Stream model for filtered streams."""
    __tablename__ = 'streams'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    rules = db.Column(db.Text, nullable=False)  # JSON string of rules

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_run = db.Column(db.DateTime, nullable=True)

    # Status
    active = db.Column(db.Boolean, default=False)

    # Relationship
    results = db.relationship('StreamResult', backref='stream', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Stream {self.name}>'

    @property
    def rules_list(self):
        """Get rules as a list of dictionaries."""
        if self.rules:
            return json.loads(self.rules)
        return []

    @rules_list.setter
    def rules_list(self, rules_data):
        """Set rules from a list of dictionaries."""
        if rules_data:
            self.rules = json.dumps(rules_data)
        else:
            self.rules = json.dumps([])


class StreamResult(db.Model):
    """Results from a stream."""
    __tablename__ = 'stream_results'

    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('streams.id'), nullable=False)
    tweet_id = db.Column(db.String(64), nullable=False)
    tweet_text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Additional data could be stored as JSON
    data = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<StreamResult {self.id}>'

    @property
    def extra_data(self):
        """Get additional data as a dictionary."""
        if self.data:
            return json.loads(self.data)
        return {}

    @extra_data.setter
    def extra_data(self, data):
        """Set additional data from a dictionary."""
        if data:
            self.data = json.dumps(data)
        else:
            self.data = None


class QuotaUsage(db.Model):
    """Track API quota usage."""
    __tablename__ = 'quota_usage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    posts_used = db.Column(db.Integer, default=0)
    reset_date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD

    __table_args__ = (
        db.UniqueConstraint('user_id', 'month', 'year', name='_user_month_year_uc'),
    )

    def __repr__(self):
        return f'<QuotaUsage {self.year}-{self.month}: {self.posts_used}/1500>'
