"""Provider management routes for providers to manage their services and bookings"""

from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.provider_service import ProviderService
from app.utils.decorators import provider_required
from app.utils.errors import AppError
from app.utils.helpers import serialize_document, is_valid_object_id, pagination_params

provider_bp = Blueprint('provider', __name__, url_prefix='/api/provider')


# ============ PROVIDER SERVICES MANAGEMENT ============

@provider_bp.route('/services', methods=['GET'])
@login_required
@provider_required
def get_provider_services():
    """Get all services offered by the provider"""
    try:
        params = pagination_params(request)

        services, total = ProviderService.get_provider_services(
            current_user.get_id(),
            skip=params['skip'],
            limit=params['limit']
        )

        services_data = [serialize_document(s) for s in services]

        return {
            'message': 'Services retrieved successfully',
            'data': {
                'services': services_data,
                'pagination': {
                    'page': params['page'],
                    'limit': params['limit'],
                    'total': total
                }
            }
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@provider_bp.route('/services', methods=['POST'])
@login_required
@provider_required
def create_provider_service():
    """Create a new service offering"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        service = ProviderService.create_provider_service(
            current_user.get_id(), data)

        return {
            'message': 'Service created successfully',
            'data': {
                'service': service
            }
        }, 201

    except ValueError as e:
        return {'error': str(e), 'code': 'VALIDATION_ERROR'}, 400
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@provider_bp.route('/services/<service_id>', methods=['PUT'])
@login_required
@provider_required
def update_provider_service(service_id):
    """Update a provider's service"""
    try:
        if not is_valid_object_id(service_id):
            return {'error': 'Invalid service ID', 'code': 'INVALID_ID'}, 400

        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        service = ProviderService.update_provider_service(
            current_user.get_id(), service_id, data)

        return {
            'message': 'Service updated successfully',
            'data': {
                'service': service
            }
        }, 200

    except ValueError as e:
        return {'error': str(e), 'code': 'NOT_FOUND'}, 404
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@provider_bp.route('/services/<service_id>', methods=['DELETE'])
@login_required
@provider_required
def delete_provider_service(service_id):
    """Delete a provider's service"""
    try:
        if not is_valid_object_id(service_id):
            return {'error': 'Invalid service ID', 'code': 'INVALID_ID'}, 400

        ProviderService.delete_provider_service(
            current_user.get_id(), service_id)

        return {
            'message': 'Service deleted successfully'
        }, 200

    except ValueError as e:
        return {'error': str(e), 'code': 'NOT_FOUND'}, 404
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


# ============ PROVIDER BOOKINGS MANAGEMENT ============

@provider_bp.route('/bookings', methods=['GET'])
@login_required
@provider_required
def get_provider_bookings():
    """Get all bookings for the provider"""
    try:
        params = pagination_params(request)
        status = request.args.get('status')

        bookings, total = ProviderService.get_provider_bookings(
            current_user.get_id(),
            status=status,
            skip=params['skip'],
            limit=params['limit']
        )

        bookings_data = [serialize_document(b) for b in bookings]

        return {
            'message': 'Bookings retrieved successfully',
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


@provider_bp.route('/bookings/<booking_id>', methods=['GET'])
@login_required
@provider_required
def get_booking_detail(booking_id):
    """Get booking details"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        booking = ProviderService.get_booking_detail(
            current_user.get_id(), booking_id)

        return {
            'message': 'Booking retrieved successfully',
            'data': {
                'booking': serialize_document(booking)
            }
        }, 200

    except ValueError as e:
        return {'error': str(e), 'code': 'NOT_FOUND'}, 404
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@provider_bp.route('/bookings/<booking_id>/confirm', methods=['POST'])
@login_required
@provider_required
def confirm_booking(booking_id):
    """Confirm/accept a booking"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        ProviderService.confirm_booking(current_user.get_id(), booking_id)

        return {
            'message': 'Booking confirmed successfully'
        }, 200

    except ValueError as e:
        return {'error': str(e), 'code': 'NOT_FOUND'}, 404
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@provider_bp.route('/bookings/<booking_id>/start', methods=['POST'])
@login_required
@provider_required
def start_booking(booking_id):
    """Start work on a booking"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        ProviderService.start_booking(current_user.get_id(), booking_id)

        return {
            'message': 'Booking started successfully'
        }, 200

    except ValueError as e:
        return {'error': str(e), 'code': 'NOT_FOUND'}, 404
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@provider_bp.route('/bookings/<booking_id>/complete', methods=['POST'])
@login_required
@provider_required
def complete_booking(booking_id):
    """Complete a booking"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        data = request.get_json() if request.is_json else {}

        ProviderService.complete_booking(
            current_user.get_id(), booking_id, data)

        return {
            'message': 'Booking completed successfully'
        }, 200

    except ValueError as e:
        return {'error': str(e), 'code': 'NOT_FOUND'}, 404
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@provider_bp.route('/bookings/<booking_id>/cancel', methods=['POST'])
@login_required
@provider_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        data = request.get_json() if request.is_json else {}
        reason = data.get('reason') if data else None

        ProviderService.cancel_booking(
            current_user.get_id(), booking_id, reason)

        return {
            'message': 'Booking cancelled successfully'
        }, 200

    except ValueError as e:
        return {'error': str(e), 'code': 'NOT_FOUND'}, 404
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


# ============ PROVIDER STATISTICS ============

@provider_bp.route('/stats', methods=['GET'])
@login_required
@provider_required
def get_provider_stats():
    """Get provider statistics"""
    try:
        stats = ProviderService.get_provider_stats(current_user.get_id())

        return {
            'message': 'Statistics retrieved successfully',
            'data': stats
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
