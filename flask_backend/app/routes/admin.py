"""Admin management routes"""

from flask import Blueprint, request
from flask_login import current_user, login_required
from app.services.admin_service import AdminService
from app.services.service_service import ServiceService
from app.utils.decorators import admin_required
from app.utils.errors import AppError
from app.utils.helpers import serialize_document, is_valid_object_id, pagination_params

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def get_all_bookings():
    """Get all bookings (admin only)"""
    try:
        # Get pagination params
        params = pagination_params(request)

        # Get status filter if provided
        status = request.args.get('status')

        bookings, total = AdminService.get_all_bookings(
            status=status, skip=params['skip'], limit=params['limit'])

        # Serialize bookings
        bookings_data = [serialize_document(b.to_dict()) for b in bookings]

        return {
            'message': 'All bookings retrieved successfully',
            'data': {
                'bookings': bookings_data,
                'pagination': {
                    'page': params['page'],
                    'limit': params['limit'],
                    'total': total
                }
            }
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    try:
        # Get pagination params
        params = pagination_params(request)

        # Get role filter if provided
        role = request.args.get('role')

        users, total = AdminService.get_all_users(
            role=role, skip=params['skip'], limit=params['limit'])

        # Serialize users
        users_data = [serialize_document(u.to_dict()) for u in users]

        return {
            'message': 'All users retrieved successfully',
            'data': {
                'users': users_data,
                'pagination': {
                    'page': params['page'],
                    'limit': params['limit'],
                    'total': total
                }
            }
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_system_stats():
    """Get system statistics (admin only)"""
    try:
        stats = AdminService.get_system_stats()

        return {
            'message': 'System statistics retrieved successfully',
            'data': stats
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@admin_bp.route('/bookings/breakdown', methods=['GET'])
@admin_required
def get_booking_breakdown():
    """Get booking breakdown by status (admin only)"""
    try:
        breakdown = AdminService.get_booking_breakdown()

        return {
            'message': 'Booking breakdown retrieved successfully',
            'data': breakdown
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@admin_bp.route('/providers/performance', methods=['GET'])
@admin_required
def get_provider_performance():
    """Get top performing providers (admin only)"""
    try:
        providers = AdminService.get_provider_performance()

        return {
            'message': 'Provider performance retrieved successfully',
            'data': {
                'providers': providers
            }
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@admin_bp.route('/users/<user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate a user (admin only)"""
    try:
        if not is_valid_object_id(user_id):
            return {'error': 'Invalid user ID', 'code': 'INVALID_ID'}, 400

        user = AdminService.deactivate_user(user_id)

        return {
            'message': 'User deactivated successfully',
            'data': {
                'user': serialize_document(user.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    """Activate a user (admin only)"""
    try:
        if not is_valid_object_id(user_id):
            return {'error': 'Invalid user ID', 'code': 'INVALID_ID'}, 400

        user = AdminService.activate_user(user_id)

        return {
            'message': 'User activated successfully',
            'data': {
                'user': serialize_document(user.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


# Service category management (also available via /api/services but repeated here for admin clarity)
@admin_bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    """Create a service category (admin only)"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        category = ServiceService.create_category(data)

        return {
            'message': 'Category created successfully',
            'data': {
                'category': serialize_document(category.to_dict())
            }
        }, 201

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@admin_bp.route('/categories/<category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """Update a service category (admin only)"""
    try:
        if not is_valid_object_id(category_id):
            return {'error': 'Invalid category ID', 'code': 'INVALID_ID'}, 400

        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        category = ServiceService.update_category(category_id, data)

        return {
            'message': 'Category updated successfully',
            'data': {
                'category': serialize_document(category.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@admin_bp.route('/categories/<category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """Delete a service category (admin only)"""
    try:
        if not is_valid_object_id(category_id):
            return {'error': 'Invalid category ID', 'code': 'INVALID_ID'}, 400

        ServiceService.delete_category(category_id)

        return {
            'message': 'Category deleted successfully'
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
