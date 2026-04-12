"""User profile routes"""

from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models.user import User
from app.models.rating import Rating
from app.services.auth_service import AuthService
from app.utils.errors import AppError, NotFoundError
from app.utils.helpers import serialize_document, is_valid_object_id, pagination_params

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile by ID"""
    try:
        if not is_valid_object_id(user_id):
            raise NotFoundError('Invalid user ID')

        user = User.find_by_id(user_id)

        if not user:
            raise NotFoundError('User not found')

        return {
            'message': 'User retrieved successfully',
            'data': {
                'user': serialize_document(user.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@users_bp.route('/<user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update user profile"""
    try:
        if not is_valid_object_id(user_id):
            raise NotFoundError('Invalid user ID')

        # Users can only update their own profile
        if current_user.get_id() != user_id:
            return {'error': 'Cannot update other user profile', 'code': 'FORBIDDEN'}, 403

        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        user = AuthService.update_profile(current_user, data)

        return {
            'message': 'Profile updated successfully',
            'data': {
                'user': serialize_document(user.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@users_bp.route('/<user_id>/profile', methods=['GET'])
def get_profile(user_id):
    """Get user profile (alias for GET /<user_id>)"""
    return get_user(user_id)


@users_bp.route('/<user_id>/ratings', methods=['GET'])
def get_user_ratings(user_id):
    """Get all ratings for a provider"""
    try:
        if not is_valid_object_id(user_id):
            raise NotFoundError('Invalid user ID')

        # Verify user exists
        user = User.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found')

        # Get pagination params
        params = pagination_params(request)

        # Get ratings
        ratings = Rating.find_by_provider(
            user_id, skip=params['skip'], limit=params['limit'])
        avg_rating, total_count = Rating.get_provider_average_rating(user_id)

        # Serialize ratings
        ratings_data = [serialize_document(r.to_dict()) for r in ratings]

        return {
            'message': 'Ratings retrieved successfully',
            'data': {
                'ratings': ratings_data,
                'averageRating': round(avg_rating, 2),
                'totalRatings': total_count,
                'pagination': {
                    'page': params['page'],
                    'limit': params['limit'],
                    'total': total_count
                }
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@users_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current authenticated user"""
    try:
        return {
            'message': 'Current user retrieved',
            'data': {
                'user': serialize_document(current_user.to_dict())
            }
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@users_bp.route('/me/profile', methods=['PUT'])
@login_required
def update_current_user():
    """Update current user profile"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        user = AuthService.update_profile(current_user, data)

        return {
            'message': 'Profile updated successfully',
            'data': {
                'user': serialize_document(user.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
