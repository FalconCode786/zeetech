"""Booking management routes"""

from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.booking_service import BookingService
from app.utils.decorators import provider_required, customer_required
from app.utils.errors import AppError
from app.utils.helpers import serialize_document, is_valid_object_id, pagination_params

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')


@bookings_bp.route('', methods=['POST'])
@login_required
def create_booking():
    """Create a new booking (customer only)"""
    try:
        # Ensure user is a customer
        if current_user.role != 'customer':
            return {'error': 'Only customers can create bookings', 'code': 'FORBIDDEN'}, 403

        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        booking = BookingService.create_booking(current_user.get_id(), data)

        return {
            'message': 'Booking created successfully',
            'data': {
                'booking': serialize_document(booking.to_dict())
            }
        }, 201

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@bookings_bp.route('', methods=['GET'])
@login_required
def list_bookings():
    """List user's bookings"""
    try:
        # Get pagination params
        params = pagination_params(request)

        # Get status filter if provided
        status = request.args.get('status')

        if current_user.role == 'customer':
            # Customers see their own bookings
            bookings, total = BookingService.list_customer_bookings(
                current_user.get_id(),
                status=status,
                skip=params['skip'],
                limit=params['limit']
            )
        else:
            return {'error': 'Invalid role', 'code': 'FORBIDDEN'}, 403

        # Serialize bookings
        bookings_data = [serialize_document(b.to_dict()) for b in bookings]

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


@bookings_bp.route('/<booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """Get booking details"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        booking = BookingService.get_booking(booking_id)

        # Check authorization - customers can only see their own bookings
        # Providers can see bookings they're assigned to
        # Admins can see all bookings
        if current_user.role == 'customer':
            if str(booking.customer_id) != current_user.get_id():
                return {'error': 'Cannot access other bookings', 'code': 'FORBIDDEN'}, 403
        elif current_user.role == 'provider':
            if str(booking.provider_id) != current_user.get_id():
                return {'error': 'Cannot access other bookings', 'code': 'FORBIDDEN'}, 403

        return {
            'message': 'Booking retrieved successfully',
            'data': {
                'booking': serialize_document(booking.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@bookings_bp.route('/<booking_id>', methods=['PUT'])
@login_required
def update_booking(booking_id):
    """Update booking details"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        booking = BookingService.get_booking(booking_id)

        # Authorization check
        if current_user.role == 'customer':
            if str(booking.customer_id) != current_user.get_id():
                return {'error': 'Cannot update other bookings', 'code': 'FORBIDDEN'}, 403
        elif current_user.role == 'provider':
            if str(booking.provider_id) != current_user.get_id():
                return {'error': 'Cannot update other bookings', 'code': 'FORBIDDEN'}, 403

        # Update allowed fields
        if 'status' in data:
            booking = BookingService.update_booking_status(
                booking_id, data['status'])

        if 'additionalCharges' in data:
            booking = BookingService.update_additional_charges(
                booking_id, data['additionalCharges'])

        if 'discountAmount' in data:
            booking = BookingService.apply_discount(
                booking_id, data['discountAmount'])

        if 'problemDescription' in data:
            booking.problem_description = data['problemDescription']
            booking.save()

        if 'specialInstructions' in data:
            booking.special_instructions = data['specialInstructions']
            booking.save()

        return {
            'message': 'Booking updated successfully',
            'data': {
                'booking': serialize_document(booking.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@bookings_bp.route('/<booking_id>/status', methods=['PUT'])
@login_required
def update_status(booking_id):
    """Update booking status"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        data = request.get_json()

        if not data or 'status' not in data:
            return {'error': 'Status is required', 'code': 'INVALID_REQUEST'}, 400

        booking = BookingService.get_booking(booking_id)

        # Only customers and assigned providers can update status
        if current_user.role == 'customer':
            if str(booking.customer_id) != current_user.get_id():
                return {'error': 'Cannot update other bookings', 'code': 'FORBIDDEN'}, 403
        elif current_user.role == 'provider':
            if str(booking.provider_id) != current_user.get_id():
                return {'error': 'You are not assigned to this booking', 'code': 'FORBIDDEN'}, 403

        booking = BookingService.update_booking_status(
            booking_id, data['status'])

        return {
            'message': 'Status updated successfully',
            'data': {
                'booking': serialize_document(booking.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@bookings_bp.route('/<booking_id>/assign-provider', methods=['PUT'])
@login_required
def assign_provider(booking_id):
    """Assign a provider to booking (admin only)"""
    try:
        if current_user.role != 'admin':
            return {'error': 'Admin access required', 'code': 'FORBIDDEN'}, 403

        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        data = request.get_json()

        if not data or 'providerId' not in data:
            return {'error': 'Provider ID is required', 'code': 'INVALID_REQUEST'}, 400

        booking = BookingService.assign_provider(
            booking_id, data['providerId'])

        return {
            'message': 'Provider assigned successfully',
            'data': {
                'booking': serialize_document(booking.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
