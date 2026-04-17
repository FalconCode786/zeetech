"""Provider dashboard and management routes."""
from typing import Optional
from flask import Blueprint, request
from app.utils.supabase_client import get_supabase
from app.utils.helpers import format_response, format_error, get_authenticated_user_id

provider_bp = Blueprint('provider', __name__)


def _require_provider_user_id():
    user_id = get_authenticated_user_id(request)
    if not user_id:
        return None, format_error('Unauthorized', 'AUTH_ERROR', 401)
    return user_id, None


def _format_provider_service(service: dict) -> dict:
    return {
        '_id': service.get('id'),
        'id': service.get('id'),
        'providerId': service.get('provider_id'),
        'provider_id': service.get('provider_id'),
        'subcategoryName': service.get('subcategory_name') or service.get('subcategoryName') or '',
        'subcategory_name': service.get('subcategory_name') or service.get('subcategoryName') or '',
        'price': service.get('price', 0),
        'description': service.get('description'),
        'status': service.get('status', 'active'),
        'createdAt': service.get('created_at') or service.get('createdAt'),
        'created_at': service.get('created_at') or service.get('createdAt'),
    }


def _format_provider_booking(booking: dict) -> dict:
    return {
        '_id': booking.get('id'),
        'id': booking.get('id'),
        'customerId': booking.get('customer_id'),
        'customer_id': booking.get('customer_id'),
        'subcategoryName': booking.get('subcategory_name') or booking.get('subcategoryName') or '',
        'subcategory_name': booking.get('subcategory_name') or booking.get('subcategoryName') or '',
        'baseAmount': booking.get('base_amount', 0),
        'base_amount': booking.get('base_amount', 0),
        'additionalCharges': booking.get('additional_charges', 0),
        'additional_charges': booking.get('additional_charges', 0),
        'discountAmount': booking.get('discount_amount', 0),
        'discount_amount': booking.get('discount_amount', 0),
        'status': booking.get('status', 'pending'),
        'problemDescription': booking.get('problem_description'),
        'problem_description': booking.get('problem_description'),
        'preferredDate': booking.get('preferred_date'),
        'preferred_date': booking.get('preferred_date'),
        'preferredTimeSlot': booking.get('preferred_time_slot'),
        'preferred_time_slot': booking.get('preferred_time_slot'),
        'location': {
            'address': booking.get('address'),
            'city': booking.get('city'),
            'area': booking.get('area'),
        },
        'createdAt': booking.get('created_at') or booking.get('createdAt'),
        'created_at': booking.get('created_at') or booking.get('createdAt'),
    }


@provider_bp.route('/services', methods=['GET', 'OPTIONS'])
def get_provider_services():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        provider_id, error = _require_provider_user_id()
        if error:
            return error

        supabase = get_supabase()
        result = supabase.table('services').select(
            '*').eq('provider_id', provider_id).order('created_at', desc=True).execute()
        services = result.data if result and hasattr(
            result, 'data') and result.data else []

        return format_response(
            'Provider services retrieved',
            {'services': [_format_provider_service(
                item) for item in services]},
            'SUCCESS',
            200,
        )
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/services', methods=['POST', 'OPTIONS'])
def create_provider_service():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        provider_id, error = _require_provider_user_id()
        if error:
            return error

        payload = request.get_json() or {}
        subcategory_name = payload.get(
            'subcategoryName') or payload.get('subcategory_name')
        price = payload.get('price')

        if not subcategory_name:
            return format_error('subcategoryName is required', 'VALIDATION_ERROR', 400)

        if price is None:
            return format_error('price is required', 'VALIDATION_ERROR', 400)

        try:
            price = float(price)
        except (TypeError, ValueError):
            return format_error('price must be a number', 'VALIDATION_ERROR', 400)

        service_data = {
            'provider_id': provider_id,
            'subcategory_name': subcategory_name,
            'price': price,
            'description': payload.get('description'),
            'status': payload.get('status', 'active'),
        }

        supabase = get_supabase()
        result = supabase.table('services').insert(service_data).execute()
        created = result.data[0] if result and hasattr(
            result, 'data') and result.data else service_data

        return format_response('Service created', {'service': _format_provider_service(created)}, 'SUCCESS', 201)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/services/<service_id>', methods=['PUT', 'OPTIONS'])
def update_provider_service(service_id):
    if request.method == 'OPTIONS':
        return '', 204

    try:
        provider_id, error = _require_provider_user_id()
        if error:
            return error

        payload = request.get_json() or {}
        update_data = {}

        if payload.get('subcategoryName') is not None:
            update_data['subcategory_name'] = payload.get('subcategoryName')
        if payload.get('description') is not None:
            update_data['description'] = payload.get('description')
        if payload.get('status') is not None:
            update_data['status'] = payload.get('status')
        if payload.get('price') is not None:
            try:
                update_data['price'] = float(payload.get('price'))
            except (TypeError, ValueError):
                return format_error('price must be a number', 'VALIDATION_ERROR', 400)

        if not update_data:
            return format_error('No valid fields provided', 'VALIDATION_ERROR', 400)

        supabase = get_supabase()
        result = (
            supabase.table('services')
            .update(update_data)
            .eq('id', service_id)
            .eq('provider_id', provider_id)
            .execute()
        )
        service = result.data[0] if result and hasattr(
            result, 'data') and result.data else None

        if not service:
            return format_error('Service not found', 'NOT_FOUND', 404)

        return format_response('Service updated', {'service': _format_provider_service(service)}, 'SUCCESS', 200)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/services/<service_id>', methods=['DELETE', 'OPTIONS'])
def delete_provider_service(service_id):
    if request.method == 'OPTIONS':
        return '', 204

    try:
        provider_id, error = _require_provider_user_id()
        if error:
            return error

        supabase = get_supabase()
        result = supabase.table('services').delete().eq(
            'id', service_id).eq('provider_id', provider_id).execute()
        deleted = result.data if result and hasattr(result, 'data') else None

        if not deleted:
            return format_error('Service not found', 'NOT_FOUND', 404)

        return format_response('Service deleted', None, 'SUCCESS', 200)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/bookings', methods=['GET', 'OPTIONS'])
def get_provider_bookings():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        provider_id, error = _require_provider_user_id()
        if error:
            return error

        status = request.args.get('status')

        supabase = get_supabase()
        query = supabase.table('bookings').select(
            '*').eq('provider_id', provider_id)
        if status:
            query = query.eq('status', status)
        result = query.order('created_at', desc=True).execute()
        bookings = result.data if result and hasattr(
            result, 'data') and result.data else []

        return format_response(
            'Provider bookings retrieved',
            {'bookings': [_format_provider_booking(
                item) for item in bookings]},
            'SUCCESS',
            200,
        )
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/bookings/<booking_id>', methods=['GET', 'OPTIONS'])
def get_provider_booking_detail(booking_id):
    if request.method == 'OPTIONS':
        return '', 204

    try:
        provider_id, error = _require_provider_user_id()
        if error:
            return error

        supabase = get_supabase()
        result = (
            supabase.table('bookings')
            .select('*')
            .eq('id', booking_id)
            .eq('provider_id', provider_id)
            .maybe_single()
            .execute()
        )
        booking = result.data if result and hasattr(result, 'data') else None

        if not booking:
            return format_error('Booking not found', 'NOT_FOUND', 404)

        return format_response('Booking retrieved', {'booking': _format_provider_booking(booking)}, 'SUCCESS', 200)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


def _update_booking_status_for_provider(booking_id: str, status: str, extra_fields: Optional[dict] = None):
    provider_id, error = _require_provider_user_id()
    if error:
        return error

    update_data = {'status': status}
    if extra_fields:
        update_data.update(extra_fields)

    supabase = get_supabase()
    result = (
        supabase.table('bookings')
        .update(update_data)
        .eq('id', booking_id)
        .eq('provider_id', provider_id)
        .execute()
    )
    booking = result.data[0] if result and hasattr(
        result, 'data') and result.data else None
    if not booking:
        return format_error('Booking not found', 'NOT_FOUND', 404)

    return format_response('Booking status updated', {'booking': _format_provider_booking(booking)}, 'SUCCESS', 200)


@provider_bp.route('/bookings/<booking_id>/confirm', methods=['POST', 'OPTIONS'])
def confirm_booking(booking_id):
    if request.method == 'OPTIONS':
        return '', 204

    try:
        return _update_booking_status_for_provider(booking_id, 'confirmed')
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/bookings/<booking_id>/start', methods=['POST', 'OPTIONS'])
def start_booking(booking_id):
    if request.method == 'OPTIONS':
        return '', 204

    try:
        return _update_booking_status_for_provider(booking_id, 'in_progress')
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/bookings/<booking_id>/complete', methods=['POST', 'OPTIONS'])
def complete_booking(booking_id):
    if request.method == 'OPTIONS':
        return '', 204

    try:
        payload = request.get_json() or {}
        additional = payload.get('additionalCharges')
        extra_fields = {}
        if additional is not None:
            try:
                extra_fields['additional_charges'] = float(additional)
            except (TypeError, ValueError):
                return format_error('additionalCharges must be a number', 'VALIDATION_ERROR', 400)

        return _update_booking_status_for_provider(booking_id, 'completed', extra_fields)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/bookings/<booking_id>/cancel', methods=['POST', 'OPTIONS'])
def cancel_booking(booking_id):
    if request.method == 'OPTIONS':
        return '', 204

    try:
        payload = request.get_json() or {}
        reason = payload.get('reason')
        extra_fields = {'cancellation_reason': reason} if reason else None
        return _update_booking_status_for_provider(booking_id, 'cancelled', extra_fields)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)


@provider_bp.route('/stats', methods=['GET', 'OPTIONS'])
def get_provider_stats():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        provider_id, error = _require_provider_user_id()
        if error:
            return error

        supabase = get_supabase()
        result = supabase.table('bookings').select(
            'status').eq('provider_id', provider_id).execute()
        bookings = result.data if result and hasattr(
            result, 'data') and result.data else []

        total = len(bookings)
        completed = len(
            [b for b in bookings if b.get('status') == 'completed'])
        pending = len([b for b in bookings if b.get('status')
                      in {'pending', 'assigned', 'confirmed'}])
        in_progress = len(
            [b for b in bookings if b.get('status') == 'in_progress'])

        stats = {
            'totalBookings': total,
            'completedBookings': completed,
            'pendingBookings': pending,
            'inProgress': in_progress,
        }

        return format_response('Provider stats retrieved', stats, 'SUCCESS', 200)
    except Exception as e:
        return format_error(str(e), 'INTERNAL_ERROR', 500)
