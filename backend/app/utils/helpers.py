"""Helper functions for the application."""
import re
import json
import jwt
from datetime import datetime
from typing import Optional


def format_response(message: str, data=None, code: str = 'SUCCESS', status_code: int = 200):
    """Format standard API response."""
    response = {
        'success': 200 <= status_code < 300,
        'message': message,
        'code': code,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    return response, status_code


def format_error(error_message: str, code: str = 'ERROR', status_code: int = 400):
    """Format standard error response."""
    response = {
        'success': False,
        'error': error_message,
        'code': code,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    return response, status_code


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Basic phone validation - at least 10 digits
    digits = ''.join(c for c in phone if c.isdigit())
    return len(digits) >= 10


def normalize_phone(phone: str) -> str:
    """Normalize phone number format."""
    # Remove all non-digit characters
    normalized = ''.join(c for c in phone if c.isdigit())

    # Add country code if not present (Pakistan: +92)
    if len(normalized) == 10 and normalized.startswith('3'):
        normalized = '92' + normalized
    elif len(normalized) == 11 and normalized.startswith('03'):
        normalized = '92' + normalized[1:]

    return normalized


def is_valid_password(password: str) -> bool:
    """
    Validate password strength.
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

    return has_upper and has_lower and has_digit and has_special


def validate_registration_data(data: dict) -> tuple[bool, str]:
    """Validate registration data."""
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    fullName = data.get('fullName', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'customer')

    if not email or not is_valid_email(email):
        return False, 'Valid email is required'

    if not phone or not is_valid_phone(phone):
        return False, 'Valid phone number is required'

    if not fullName or len(fullName) < 2:
        return False, 'Full name is required (minimum 2 characters)'

    if not password or not is_valid_password(password):
        return False, 'Password must be at least 8 characters with uppercase, lowercase, digit, and special character'

    if role not in ['customer', 'provider']:
        return False, 'Role must be customer or provider'

    return True, ''


def validate_login_data(data: dict) -> tuple[bool, str]:
    """Validate login data."""
    email_or_phone = data.get('email') or data.get('phone')
    password = data.get('password', '')

    if not email_or_phone:
        return False, 'Email or phone is required'

    if not password:
        return False, 'Password is required'

    return True, ''


def extract_bearer_token(req) -> Optional[str]:
    """Extract bearer token from Authorization header."""
    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ', 1)[1].strip()


def decode_auth_token(token: str) -> Optional[dict]:
    """Decode JWT token and return payload or None."""
    if not token:
        return None

    from app.config import Config

    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    except Exception:
        return None


def get_authenticated_user_id(req) -> Optional[str]:
    """Get authenticated user id from request JWT token."""
    token = extract_bearer_token(req)
    payload = decode_auth_token(token) if token else None
    return payload.get('userId') if payload else None
