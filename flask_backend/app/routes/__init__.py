"""Routes initialization - Register all blueprints"""


def register_blueprints(app):
    """Register all route blueprints with the Flask app"""

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'ZeeTech Backend is running'}, 200

    # Phase 3: Auth routes
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Phase 3: User routes
    from app.routes.users import users_bp
    app.register_blueprint(users_bp)

    # Phase 4: Service routes
    from app.routes.services import services_bp
    app.register_blueprint(services_bp)

    # Phase 5: Booking routes
    from app.routes.bookings import bookings_bp
    app.register_blueprint(bookings_bp)

    # Phase 6: Provider routes
    from app.routes.provider import provider_bp
    app.register_blueprint(provider_bp)

    # Phase 6: Rating routes
    from app.routes.ratings import ratings_bp
    app.register_blueprint(ratings_bp)

    # Phase 7: Feedback routes (required before payment)
    from app.routes.feedbacks import feedbacks_bp
    app.register_blueprint(feedbacks_bp)

    # Phase 7: Payment routes
    from app.routes.payments import payments_bp
    app.register_blueprint(payments_bp)

    # Phase 7: Admin routes
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Phase 7: Upload routes
    from app.routes.uploads import uploads_bp
    app.register_blueprint(uploads_bp)
