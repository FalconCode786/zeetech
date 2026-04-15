"""Decorators for authentication and authorization"""

from functools import wraps
from flask_login import current_user
from flask import request, current_app
from app.utils.errors import UnauthorizedError, ForbiddenError
import jwt
import os


def _get_user_from_token():
    """Extract and validate JWT token from Authorization header"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]  # Remove 'Bearer ' prefix
        secret_key = current_app.config.get(
            'SECRET_KEY', os.environ.get('SECRET_KEY', 'your-secret-key'))

        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError('Token has expired')
        except jwt.InvalidTokenError:
            raise UnauthorizedError('Invalid token')
    except UnauthorizedError:
        raise
    except Exception:
        return None


def _is_authenticated():
    """Check if user is authenticated via session or JWT token"""
    # First check Flask-Login session
    if current_user.is_authenticated:
        return True

    # Then check JWT token
    try:
        token_data = _get_user_from_token()
        return token_data is not None
    except Exception:
        return False


def _get_user_role():
    """Get user role from session or JWT token"""
    if current_user.is_authenticated:
        return getattr(current_user, 'role', None)

    try:
        token_data = _get_user_from_token()
        if token_data:
            return token_data.get('role')
    except Exception:
        pass

    return None


def _get_user_id():
    """Get user ID from session or JWT token"""
    if current_user.is_authenticated:
        return current_user.get_id()

    try:
        token_data = _get_user_from_token()
        if token_data:
            return token_data.get('user_id')
    except Exception:
        pass

    return None


def login_required_api(f):
    """Decorator to require login for API endpoints (session or JWT)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not _is_authenticated():
            return {'error': 'Login required', 'code': 'UNAUTHORIZED'}, 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role (session or JWT)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not _is_authenticated():
            return {'error': 'Login required', 'code': 'UNAUTHORIZED'}, 401

        role = _get_user_role()
        if role != 'admin':
            return {'error': 'Admin access required', 'code': 'FORBIDDEN'}, 403
        return f(*args, **kwargs)
    return decorated_function


def provider_required(f):
    """Decorator to require provider role (or admin) - supports session or JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not _is_authenticated():
            return {'error': 'Login required', 'code': 'UNAUTHORIZED'}, 401

        role = _get_user_role()
        if role not in ['provider', 'admin']:
            return {'error': 'Provider access required', 'code': 'FORBIDDEN'}, 403
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    """Decorator to require customer role - supports session or JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not _is_authenticated():
            return {'error': 'Login required', 'code': 'UNAUTHORIZED'}, 401

        role = _get_user_role()
        if role != 'customer':
            return {'error': 'Customer access required', 'code': 'FORBIDDEN'}, 403
        return f(*args, **kwargs)
    return decorated_function
