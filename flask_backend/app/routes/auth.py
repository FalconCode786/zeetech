"""Authentication routes"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from app.services.auth_service import AuthService
from app.utils.errors import AppError
from app.utils.helpers import serialize_document, format_response

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        email = data.get('email')
        phone = data.get('phone')
        full_name = data.get('fullName')
        password = data.get('password')
        role = data.get('role', 'customer')

        # Register user
        user = AuthService.register(email, phone, full_name, password, role)

        # Log user in
        login_user(user)

        return {
            'message': 'User registered successfully',
            'data': {
                'user': serialize_document(user.to_dict())
            }
        }, 201

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        email_or_phone = data.get('email') or data.get('phone')
        password = data.get('password')

        if not email_or_phone or not password:
            return {'error': 'Email/phone and password required', 'code': 'MISSING_CREDENTIALS'}, 400

        # Authenticate user
        user = AuthService.login(email_or_phone, password)

        # Create session
        login_user(user, remember=data.get('rememberMe', False))

        return {
            'message': 'Login successful',
            'data': {
                'user': serialize_document(user.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        logout_user()
        return {'message': 'Logged out successfully'}, 200
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@auth_bp.route('/verify', methods=['GET'])
def verify():
    """Get authenticated user info"""
    try:
        if not current_user.is_authenticated:
            return {'error': 'Not authenticated', 'code': 'UNAUTHORIZED'}, 401

        return {
            'message': 'User verified',
            'data': {
                'user': serialize_document(current_user.to_dict())
            }
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        if not current_user.is_authenticated:
            return {'error': 'Login required', 'code': 'UNAUTHORIZED'}, 401

        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')

        AuthService.change_password(current_user, old_password, new_password)

        return {'message': 'Password changed successfully'}, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
