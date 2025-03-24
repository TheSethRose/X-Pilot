import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

from app.models import db, User
from utils.logging_config import setup_logging

def create_app(test_config=None):
    """Create and configure the Flask application using the factory pattern."""
    # Load .env file explicitly
    load_dotenv()

    # Use absolute path for template and static folders
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    app = Flask(__name__,
                instance_relative_config=True,
                template_folder=template_dir,
                static_folder=static_dir)

    # Configure session to work with ngrok
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

    # Load the default configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///twikit.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TWITTER_CONSUMER_KEY=os.getenv('CONSUMER_KEY'),
        TWITTER_CONSUMER_SECRET=os.getenv('CONSUMER_SECRET'),
        TWITTER_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'),
        TWITTER_ACCESS_TOKEN_SECRET=os.getenv('ACCESS_TOKEN_SECRET'),
        SITE_URL=os.getenv('SITE_URL', 'http://localhost:5000')
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Setup login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # type: ignore[assignment]
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Setup logging
    setup_logging(app)

    # Register blueprints
    try:
        from app.routes.auth import auth_bp
        from app.routes.main import main_bp
        from app.routes.posts import posts_bp
        from app.routes.users import users_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(posts_bp)
        app.register_blueprint(users_bp)
    except ImportError as e:
        app.logger.warning(f"Could not import blueprints: {e}")

    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Add support for ngrok by automatically setting the ngrok-skip-browser-warning header
    @app.after_request
    def add_ngrok_headers(response):
        response.headers['ngrok-skip-browser-warning'] = '1'
        return response

    return app
