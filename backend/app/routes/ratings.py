"""Ratings routes."""
import uuid
from flask import Blueprint, request
from app.utils.helpers import format_response, format_error
from app.utils.supabase_client import get_supabase
from app.utils.helpers import get_authenticated_user_id

ratings_bp = Blueprint('ratings', __name__)


@ratings_bp.route('', methods=['POST', 'OPTIONS'])
def create_rating():
    """Create a new rating."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json() or {}

        required_fields = ['booking_id', 'provider_id', 'rating']
        missing_fields = [
            field for field in required_fields if data.get(field) is None]
        if missing_fields:
            return format_error(f'Missing required fields: {", ".join(missing_fields)}', 'VALIDATION_ERROR', 400)

        try:
            rating_value = int(data.get('rating'))
        except (TypeError, ValueError):
            return format_error('rating must be an integer', 'VALIDATION_ERROR', 400)

        if rating_value < 1 or rating_value > 5:
            return format_error('rating must be between 1 and 5', 'VALIDATION_ERROR', 400)

        customer_id = get_authenticated_user_id(
            request) or data.get('customer_id')
        if not customer_id:
            return format_error('customer_id is required', 'VALIDATION_ERROR', 400)

        rating_data = {
            'id': str(uuid.uuid4()),
            'booking_id': data.get('booking_id'),
            'provider_id': data.get('provider_id'),
            'customer_id': customer_id,
            'rating': rating_value,
            'review': data.get('review') or data.get('comment'),
        }

        supabase = get_supabase()
        result = supabase.table('ratings').insert(rating_data).execute()
        created_rating = result.data[0] if result and hasattr(
            result, 'data') and result.data else rating_data

        return format_response('Rating created', created_rating, 'SUCCESS', 201)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@ratings_bp.route('/<rating_id>', methods=['GET', 'OPTIONS'])
def get_rating(rating_id):
    """Get a specific rating."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        result = supabase.table('ratings').select(
            '*').eq('id', rating_id).maybe_single().execute()
        rating = result.data if result and hasattr(result, 'data') else None

        if not rating:
            return format_error('Rating not found', 'NOT_FOUND', 404)

        return format_response('Rating retrieved', rating, 'SUCCESS', 200)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)
