from flask import Flask, request
from flask_cors import CORS
from flask_login import LoginManager
from supabase import create_client
from app.config import get_config
import os
import logging
from logging.handlers import RotatingFileHandler


# Global variables for database and extensions
supabase_client = None
login_manager = None


def create_app(config=None):
    """Application factory function"""
    global supabase_client, login_manager

    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = get_config()

    app.config.from_object(config)

    # Setup logging
    setup_logging(app)

    # Initialize CORS properly for Flutter frontend (mobile and web)
    # Allow requests from localhost (web) and all origins for mobile
    CORS(app,
         supports_credentials=True,
         origins=['*'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         max_age=3600)

    # Handle CORS preflight requests (OPTIONS) - must run before other middleware
    @app.before_request
    def handle_preflight():
        """Handle CORS preflight requests"""
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response.headers['Access-Control-Allow-Origin'] = request.headers.get(
                'Origin', '*')
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200

    # Initialize Supabase
    try:
        supabase_url = app.config.get('SUPABASE_URL')
        supabase_key = app.config.get('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            app.logger.warning(
                'SUPABASE_URL or SUPABASE_KEY not set. Running without database connection.')
        else:
            supabase_client = create_client(supabase_url, supabase_key)
            # Test connection by querying users table
            try:
                supabase_client.table('users').select('*').limit(1).execute()
                app.logger.info('Supabase connection successful')
            except Exception as table_error:
                # Tables may not exist yet - warn but don't fail
                if 'PGRST205' in str(table_error) or 'Could not find the table' in str(table_error):
                    app.logger.warning(
                        'Supabase tables not initialized. Run SUPABASE_MIGRATIONS.sql first.')
                else:
                    app.logger.warning(
                        f'Supabase test query failed: {table_error}')
    except Exception as e:
        app.logger.error(f'Supabase connection failed: {e}')

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.find_by_id(user_id)

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        """Return JSON error for API requests instead of redirecting"""
        if request.path.startswith('/api/'):
            return {
                'error': 'Authentication required',
                'code': 'UNAUTHORIZED'
            }, 401
        # For non-API requests, redirect to login
        from flask import redirect, url_for
        return redirect(url_for('auth.login', next=request.url))

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
    """Get the Supabase client instance"""
    global supabase_client
    if supabase_client is None:
        raise RuntimeError(
            'Database not initialized. Call create_app() first.')
    return supabase_client


def get_supabase_client():
    """Get the Supabase client instance"""
    global supabase_client
    if supabase_client is None:
        raise RuntimeError(
            'Supabase client not initialized. Call create_app() first.')
    return supabase_client
