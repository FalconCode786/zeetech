"""Custom exceptions for the application"""


class AppError(Exception):
    """Base application error"""

    def __init__(self, message, code=None, status_code=400):
        self.message = message
        self.code = code or 'APP_ERROR'
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppError):
    """Validation error"""

    def __init__(self, message, code='VALIDATION_ERROR'):
        super().__init__(message, code, 422)


class NotFoundError(AppError):
    """Resource not found"""

    def __init__(self, message, code='NOT_FOUND'):
        super().__init__(message, code, 404)


class UnauthorizedError(AppError):
    """Unauthorized access"""

    def __init__(self, message='Unauthorized', code='UNAUTHORIZED'):
        super().__init__(message, code, 401)


class ForbiddenError(AppError):
    """Forbidden access"""

    def __init__(self, message='Forbidden', code='FORBIDDEN'):
        super().__init__(message, code, 403)


class ConflictError(AppError):
    """Resource conflict (e.g., duplicate email)"""

    def __init__(self, message, code='CONFLICT'):
        super().__init__(message, code, 409)


class InternalError(AppError):
    """Internal server error"""

    def __init__(self, message, code='INTERNAL_ERROR'):
        super().__init__(message, code, 500)


def register_error_handlers(app):
    """Register error handlers for the Flask app"""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        """Handle custom app errors"""
        response = {
            'error': error.message,
            'code': error.code
        }
        app.logger.warning(
            f'Application error ({error.code}): {error.message}')
        return response, error.status_code

    @app.errorhandler(404)
    def handle_404(error):
        """Handle 404 errors"""
        response = {
            'error': 'Resource not found',
            'code': 'NOT_FOUND'
        }
        app.logger.info(f'404 Not Found')
        return response, 404

    @app.errorhandler(500)
    def handle_500(error):
        """Handle 500 errors"""
        response = {
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }
        app.logger.error(f'Internal server error: {error}', exc_info=True)
        return response, 500
