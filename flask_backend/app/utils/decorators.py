"""Decorators for authentication and authorization"""

from functools import wraps
from flask_login import current_user
from app.utils.errors import UnauthorizedError, ForbiddenError


def login_required_api(f):
    """Decorator to require login for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            raise UnauthorizedError('Login required')
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            raise UnauthorizedError('Login required')
        if current_user.role != 'admin':
            raise ForbiddenError('Admin access required')
        return f(*args, **kwargs)
    return decorated_function


def provider_required(f):
    """Decorator to require provider role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            raise UnauthorizedError('Login required')
        if current_user.role != 'provider':
            raise ForbiddenError('Provider access required')
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    """Decorator to require customer role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            raise UnauthorizedError('Login required')
        if current_user.role != 'customer':
            raise ForbiddenError('Customer access required')
        return f(*args, **kwargs)
    return decorated_function
