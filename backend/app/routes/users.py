"""Users routes."""
from flask import Blueprint, request
from app.utils.supabase_client import get_supabase
from app.utils.helpers import format_response, format_error, get_authenticated_user_id

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET', 'OPTIONS'])
def get_profile():
    """Get user profile."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        user_id = get_authenticated_user_id(request)
        if not user_id:
            return format_error('Unauthorized', 'AUTH_ERROR', 401)

        supabase = get_supabase()
        result = supabase.table('users').select(
            '*').eq('id', user_id).maybe_single().execute()
        user = result.data if result and hasattr(result, 'data') else None

        if not user:
            return format_error('User not found', 'NOT_FOUND', 404)

        user.pop('password', None)
        return user, 200
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@users_bp.route('/profile', methods=['PUT', 'OPTIONS'])
def update_profile():
    """Update user profile."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        user_id = get_authenticated_user_id(request)
        if not user_id:
            return format_error('Unauthorized', 'AUTH_ERROR', 401)

        payload = request.get_json() or {}
        allowed_fields = {
            'fullName', 'profileImage', 'address', 'city', 'area',
            'phone', 'status', 'emailVerified', 'phoneVerified'
        }
        update_data = {key: value for key,
                       value in payload.items() if key in allowed_fields}

        if not update_data:
            return format_error('No valid profile fields provided', 'VALIDATION_ERROR', 400)

        supabase = get_supabase()
        result = supabase.table('users').update(
            update_data).eq('id', user_id).execute()
        user = result.data[0] if result and hasattr(
            result, 'data') and result.data else None

        if not user:
            return format_error('User not found', 'NOT_FOUND', 404)

        user.pop('password', None)
        return user, 200
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)
