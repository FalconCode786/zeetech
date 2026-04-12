from flask import Flask, request
from flask_cors import CORS
from flask_login import LoginManager
from pymongo import MongoClient
from app.config import get_config
import os
import logging
from logging.handlers import RotatingFileHandler


# Global variables for database and extensions
db = None
mongo_client = None
login_manager = None


def create_app(config=None):
    """Application factory function"""
    global db, mongo_client, login_manager

    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = get_config()

    app.config.from_object(config)

    # Setup logging
    setup_logging(app)

    # Initialize CORS properly for Flutter frontend (mobile and web)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Initialize MongoDB
    mongo_client = MongoClient(app.config['MONGODB_URI'])
    db = mongo_client[app.config['MONGODB_DB_NAME']]

    # Test MongoDB connection
    try:
        mongo_client.admin.command('ping')
        app.logger.info('MongoDB connection successful')
    except Exception as e:
        app.logger.error(f'MongoDB connection failed: {e}')
        raise

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.find_by_id(user_id)

    # Create uploads folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Add request/response logging middleware
    @app.before_request
    def log_request():
        """Log incoming requests"""
        app.logger.debug(
            f'{request.remote_addr} - {request.method} {request.path}')

    @app.after_request
    def log_response(response):
        """Log response status"""
        app.logger.debug(
            f'Response: {response.status_code} for {request.method} {request.path}')
        return response

    # Register blueprints (will be created in Phase 3)
    from app.routes import register_blueprints
    register_blueprints(app)

    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    return app


def setup_logging(app):
    """Configure application logging"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/zeetech_backend.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )

    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    ))
    console_handler.setLevel(
        logging.DEBUG if app.config['DEBUG'] else logging.INFO)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.DEBUG if app.config['DEBUG'] else logging.INFO)
    app.logger.info(
        f'Logging configured for {app.config.get("FLASK_ENV", "development")} environment')


def get_db():
    """Get the MongoDB database instance"""
    global db
    if db is None:
        raise RuntimeError(
            'Database not initialized. Call create_app() first.')
    return db


def get_mongo_client():
    """Get the MongoDB client instance"""
    global mongo_client
    if mongo_client is None:
        raise RuntimeError(
            'MongoDB client not initialized. Call create_app() first.')
    return mongo_client
