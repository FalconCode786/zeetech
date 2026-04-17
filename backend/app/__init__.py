from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.getenv(
        'JWT_SECRET', 'your-secret-key-change-in-production')

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:8080",
                "http://127.0.0.1:8080",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.services import services_bp
    from app.routes.bookings import bookings_bp
    from app.routes.users import users_bp
    from app.routes.ratings import ratings_bp
    from app.routes.provider import provider_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(ratings_bp, url_prefix='/api/ratings')
    app.register_blueprint(provider_bp, url_prefix='/api/provider')

    # Health check route
    @app.route('/health', methods=['GET'])
    def health():
        return {
            'status': 'healthy',
            'message': 'ZeeTech Backend is running',
            'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }, 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Route not found',
            'code': 'NOT_FOUND',
            'path': __import__('flask').request.path
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'message': str(error)
        }, 500

    return app
