"""Services routes."""
import uuid
from flask import Blueprint, request
from app.utils.supabase_client import get_supabase
from app.utils.helpers import format_response, format_error, get_authenticated_user_id

services_bp = Blueprint('services', __name__)


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@services_bp.route('', methods=['GET', 'OPTIONS'])
def get_services():
    """Get all services."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        page = max(1, _safe_int(request.args.get('page'), 1))
        per_page = max(
            1, min(_safe_int(request.args.get('per_page'), 20), 100))
        status = request.args.get('status')
        category_id = request.args.get('category_id')
        provider_id = request.args.get('provider_id')

        query = supabase.table('services').select('*')
        if status:
            query = query.eq('status', status)
        if category_id:
            query = query.eq('category_id', category_id)
        if provider_id:
            query = query.eq('provider_id', provider_id)

        start = (page - 1) * per_page
        end = start + per_page - 1
        result = query.order('created_at', desc=True).range(
            start, end).execute()
        services = result.data if result and hasattr(
            result, 'data') and result.data else []

        return format_response('Services retrieved', services, 'SUCCESS', 200)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@services_bp.route('/<service_id>', methods=['GET', 'OPTIONS'])
def get_service(service_id):
    """Get a specific service."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        result = supabase.table('services').select(
            '*').eq('id', service_id).maybe_single().execute()
        service = result.data if result and hasattr(result, 'data') else None

        if not service:
            return format_error('Service not found', 'NOT_FOUND', 404)

        return format_response('Service retrieved', service, 'SUCCESS', 200)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@services_bp.route('', methods=['POST', 'OPTIONS'])
def create_service():
    """Create a new service."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json() or {}
        subcategory_id = data.get('subcategory_id')
        subcategory_name = data.get(
            'subcategoryName') or data.get('subcategory_name')
        price = data.get('price')
        description = data.get('description')

        if not subcategory_id and not subcategory_name:
            return format_error('subcategory_id or subcategoryName is required', 'VALIDATION_ERROR', 400)

        if price is None:
            return format_error('price is required', 'VALIDATION_ERROR', 400)

        try:
            price = float(price)
        except (TypeError, ValueError):
            return format_error('price must be a number', 'VALIDATION_ERROR', 400)

        user_id = get_authenticated_user_id(request)
        provider_id = user_id or data.get('provider_id')

        service_data = {
            'id': str(uuid.uuid4()),
            'provider_id': provider_id,
            'subcategory_id': subcategory_id,
            'subcategory_name': subcategory_name,
            'price': price,
            'description': description,
            'status': data.get('status', 'active'),
        }

        supabase = get_supabase()
        result = supabase.table('services').insert(service_data).execute()
        created_service = result.data[0] if result and hasattr(
            result, 'data') and result.data else service_data

        return format_response('Service created', created_service, 'SUCCESS', 201)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@services_bp.route('/categories', methods=['GET', 'OPTIONS'])
def get_categories():
    """Get all service categories."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        result = supabase.table('service_categories').select(
            '*').order('display_order').execute()
        categories = result.data if result and hasattr(
            result, 'data') and result.data else []
        return categories, 200
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@services_bp.route('/categories/<int:category_id>', methods=['GET', 'OPTIONS'])
def get_category_by_id(category_id):
    """Get category details."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        result = supabase.table('service_categories').select(
            '*').eq('id', category_id).maybe_single().execute()
        category = result.data if result and hasattr(result, 'data') else None
        if not category:
            return format_error('Category not found', 'NOT_FOUND', 404)
        return category, 200
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@services_bp.route('/categories/<int:category_id>/subcategories', methods=['GET', 'OPTIONS'])
def get_subcategories(category_id):
    """Get subcategories by category id."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        result = supabase.table('service_subcategories').select(
            '*').eq('category_id', category_id).order('display_order').execute()
        subcategories = result.data if result and hasattr(
            result, 'data') and result.data else []
        return subcategories, 200
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)
