"""Bookings routes."""
import uuid
from flask import Blueprint, request
from app.utils.supabase_client import get_supabase
from app.utils.helpers import format_response, format_error, get_authenticated_user_id

bookings_bp = Blueprint('bookings', __name__)


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@bookings_bp.route('', methods=['GET', 'OPTIONS'])
def get_bookings():
    """Get all bookings."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        page = max(1, _safe_int(request.args.get('page'), 1))
        per_page = max(
            1, min(_safe_int(request.args.get('per_page'), 10), 100))
        status = request.args.get('status')
        customer_id = request.args.get(
            'customer_id') or get_authenticated_user_id(request)

        query = supabase.table('bookings').select('*')
        if status:
            query = query.eq('status', status)
        if customer_id:
            query = query.eq('customer_id', customer_id)

        start = (page - 1) * per_page
        end = start + per_page - 1
        result = query.order('created_at', desc=True).range(
            start, end).execute()
        bookings = result.data if result and hasattr(
            result, 'data') and result.data else []

        return bookings, 200
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@bookings_bp.route('/<booking_id>', methods=['GET', 'OPTIONS'])
def get_booking(booking_id):
    """Get a specific booking."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        result = supabase.table('bookings').select(
            '*').eq('id', booking_id).maybe_single().execute()
        booking = result.data if result and hasattr(result, 'data') else None

        if not booking:
            return format_error('Booking not found', 'NOT_FOUND', 404)

        return booking, 200
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@bookings_bp.route('', methods=['POST', 'OPTIONS'])
def create_booking():
    """Create a new booking."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json() or {}

        required_fields = ['subcategory_id', 'address', 'city',
                           'area', 'preferred_date', 'preferred_time_slot']
        missing_fields = [
            field for field in required_fields if not data.get(field)]
        if missing_fields:
            return format_error(f'Missing required fields: {", ".join(missing_fields)}', 'VALIDATION_ERROR', 400)

        customer_id = get_authenticated_user_id(
            request) or data.get('customer_id')
        if not customer_id:
            return format_error('customer_id is required', 'VALIDATION_ERROR', 400)

        base_amount = data.get('base_amount', 0)
        additional_charges = data.get('additional_charges', 0)
        discount_amount = data.get('discount_amount', 0)

        try:
            base_amount = float(base_amount)
            additional_charges = float(additional_charges)
            discount_amount = float(discount_amount)
        except (TypeError, ValueError):
            return format_error('Amount fields must be numbers', 'VALIDATION_ERROR', 400)

        booking_data = {
            'id': str(uuid.uuid4()),
            'booking_number': f"BK-{uuid.uuid4().hex[:10].upper()}",
            'customer_id': customer_id,
            'subcategory_id': data.get('subcategory_id'),
            'provider_id': data.get('provider_id'),
            'status': data.get('status', 'pending'),
            'payment_status': data.get('payment_status', 'pending'),
            'address': data.get('address'),
            'city': data.get('city'),
            'area': data.get('area'),
            'landmark': data.get('landmark'),
            'preferred_date': data.get('preferred_date'),
            'preferred_time_slot': data.get('preferred_time_slot'),
            'base_amount': base_amount,
            'additional_charges': additional_charges,
            'discount_amount': discount_amount,
            'total_amount': base_amount + additional_charges - discount_amount,
            'problem_description': data.get('problem_description'),
            'special_instructions': data.get('special_instructions'),
        }

        supabase = get_supabase()
        result = supabase.table('bookings').insert(booking_data).execute()
        created_booking = result.data[0] if result and hasattr(
            result, 'data') and result.data else booking_data

        return created_booking, 201
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@bookings_bp.route('/<booking_id>/cancel', methods=['GET', 'OPTIONS'])
def cancel_booking(booking_id):
    """Cancel a specific booking."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        supabase = get_supabase()
        result = supabase.table('bookings').update(
            {'status': 'cancelled'}).eq('id', booking_id).execute()
        updated_booking = result.data[0] if result and hasattr(
            result, 'data') and result.data else None

        if not updated_booking:
            return format_error('Booking not found', 'NOT_FOUND', 404)

        return updated_booking, 200
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)
