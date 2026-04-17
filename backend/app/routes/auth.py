"""Authentication routes."""
from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.helpers import (
    format_response, format_error,
    validate_registration_data, validate_login_data,
    extract_bearer_token, decode_auth_token
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Register a new user."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()

        # Validate input
        is_valid, error_msg = validate_registration_data(data)
        if not is_valid:
            return format_error(error_msg, 'VALIDATION_ERROR', 400)

        # Register user
        result = AuthService.register(
            email=data['email'],
            phone=data['phone'],
            fullName=data['fullName'],
            password=data['password'],
            role=data.get('role', 'customer')
        )

        return format_response('User registered successfully', result, 'SUCCESS', 201)

    except ValueError as e:
        return format_error(str(e), 'REGISTRATION_ERROR', 400)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Login a user."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()

        # Validate input
        is_valid, error_msg = validate_login_data(data)
        if not is_valid:
            return format_error(error_msg, 'VALIDATION_ERROR', 400)

        # Login user
        email_or_phone = data.get('email') or data.get('phone')
        result = AuthService.login(
            email_or_phone=email_or_phone,
            password=data['password']
        )

        return format_response('Login successful', result, 'SUCCESS', 200)

    except ValueError as e:
        return format_error(str(e), 'LOGIN_ERROR', 401)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@auth_bp.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    """Logout a user."""
    if request.method == 'OPTIONS':
        return '', 204

    return format_response('Logged out successfully', None, 'SUCCESS', 200)


@auth_bp.route('/verify', methods=['GET', 'OPTIONS'])
def verify():
    """Verify JWT token."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        token = extract_bearer_token(request)
        if not token:
            return format_error('No token provided', 'AUTH_ERROR', 401)

        payload = decode_auth_token(token)
        if not payload:
            return format_error('Invalid or expired token', 'AUTH_ERROR', 401)

        return format_response('Token valid', {
            'userId': payload.get('userId'),
            'role': payload.get('role')
        }, 'SUCCESS', 200)

    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)
