"""Service catalog routes"""

from flask import Blueprint, request
from flask_login import login_required
from app.services.service_service import ServiceService
from app.utils.decorators import admin_required
from app.utils.errors import AppError
from app.utils.helpers import serialize_document, is_valid_object_id, pagination_params

services_bp = Blueprint('services', __name__, url_prefix='/api/services')


@services_bp.route('/categories', methods=['GET'])
def list_categories():
    """List all service categories"""
    try:
        # Get pagination params
        params = pagination_params(request)

        # Get search query if provided
        query = request.args.get('search', '').strip()

        if query:
            categories, total = ServiceService.search_categories(
                query, skip=params['skip'], limit=params['limit'])
        else:
            categories, total = ServiceService.list_categories(
                skip=params['skip'], limit=params['limit'])

        # Serialize categories
        categories_data = [serialize_document(c.to_dict()) for c in categories]

        return {
            'message': 'Categories retrieved successfully',
            'data': {
                'categories': categories_data,
                'pagination': {
                    'page': params['page'],
                    'limit': params['limit'],
                    'total': total
                }
            }
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@services_bp.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    """Get a specific service category with subcategories"""
    try:
        if not is_valid_object_id(category_id):
            return {'error': 'Invalid category ID', 'code': 'INVALID_ID'}, 400

        category = ServiceService.get_category(category_id)

        return {
            'message': 'Category retrieved successfully',
            'data': {
                'category': serialize_document(category.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@services_bp.route('/categories/<category_id>/subcategories', methods=['GET'])
def get_subcategories(category_id):
    """Get subcategories for a category"""
    try:
        if not is_valid_object_id(category_id):
            return {'error': 'Invalid category ID', 'code': 'INVALID_ID'}, 400

        subcategories = ServiceService.get_subcategories(category_id)

        return {
            'message': 'Subcategories retrieved successfully',
            'data': {
                'subcategories': serialize_document(subcategories)
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


# Admin endpoints for managing categories
@services_bp.route('/admin/categories', methods=['POST'])
def create_category():
    """Create a new service category (admin only)"""
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


@services_bp.route('/admin/categories/<category_id>', methods=['PUT'])
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


@services_bp.route('/admin/categories/<category_id>', methods=['DELETE'])
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
