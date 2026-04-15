"""Payment processing routes with multiple gateway support"""

from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.payment_gateway_service import PaymentService
from app.models.booking import Booking
from app.utils.errors import AppError

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@payments_bp.route('/initiate', methods=['POST'])
@login_required
def initiate_payment():
    """Initiate payment with specified gateway"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        booking_id = data.get('bookingId')
        # 'easypaisa', 'jazzcash', 'stripe'
        payment_method = data.get('paymentMethod')
        phone_number = data.get('phoneNumber')

        if not booking_id or not payment_method:
            return {'error': 'Booking ID and payment method are required', 'code': 'MISSING_FIELDS'}, 400

        # Verify booking
        booking = Booking.find_by_id(booking_id)
        if not booking:
            return {'error': 'Booking not found', 'code': 'NOT_FOUND'}, 404

        # Verify user is the customer
        if str(booking.customer_id) != str(current_user.id):
            return {'error': 'Unauthorized', 'code': 'FORBIDDEN'}, 403

        # Initiate payment
        result = PaymentService.create_payment(
            booking_id, payment_method, phone_number)

        return {
            'message': 'Payment initiated successfully',
            'data': result
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@payments_bp.route('/confirm', methods=['POST'])
@login_required
def confirm_payment():
    """Confirm payment and update booking"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        booking_id = data.get('bookingId')
        payment_method = data.get('paymentMethod')
        transaction_data = data.get('transactionData', {})

        if not booking_id or not payment_method:
            return {'error': 'Booking ID and payment method are required', 'code': 'MISSING_FIELDS'}, 400

        # Verify booking
        booking = Booking.find_by_id(booking_id)
        if not booking:
            return {'error': 'Booking not found', 'code': 'NOT_FOUND'}, 404

        # Verify user is the customer
        if str(booking.customer_id) != str(current_user.id):
            return {'error': 'Unauthorized', 'code': 'FORBIDDEN'}, 403

        # Confirm payment
        result = PaymentService.confirm_payment(
            booking_id, payment_method, transaction_data)

        if result['status'] == 'success':
            return {
                'message': result['message'],
                'data': result
            }, 200
        else:
            return {
                'error': result['message'],
                'data': result
            }, 400

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@payments_bp.route('/jazzcash-callback', methods=['POST', 'GET'])
def jazzcash_callback():
    """JazzCash payment callback"""
    try:
        # JazzCash sends payment response as GET/POST parameters
        ref_code = request.args.get(
            'pp_ref_code') or request.form.get('pp_ref_code')
        status_code = request.args.get(
            'pp_status') or request.form.get('pp_status')

        if not ref_code:
            return {'error': 'Invalid callback'}, 400

        # Extract booking ID from ref code
        # Format: ZT{booking_id}{timestamp}
        if ref_code.startswith('ZT'):
            booking_id = ref_code[2:].rsplit(
                '-', 1)[0] if '-' in ref_code else ref_code[2:-10]
        else:
            return {'error': 'Invalid reference code'}, 400

        booking = Booking.find_by_id(booking_id)
        if not booking:
            return {'error': 'Booking not found'}, 404

        # Update payment status based on JazzCash response
        if status_code in ['PP056', 'PP000']:  # Success codes
            booking.payment_status = 'completed'
            booking.payment_method = 'jazzcash'
            booking.payment_transaction_id = request.args.get(
                'pp_txnid') or request.form.get('pp_txnid')
            booking.save()
            return {'message': 'Payment confirmed'}, 200
        else:
            booking.payment_status = 'failed'
            booking.save()
            return {'message': 'Payment failed'}, 400

    except Exception as e:
        return {'error': str(e)}, 500


@payments_bp.route('/jazzcash-notify', methods=['POST'])
def jazzcash_notify():
    """JazzCash notification endpoint"""
    try:
        data = request.get_json() or request.form.to_dict()

        ref_code = data.get('pp_ref_code')
        if not ref_code:
            return {'error': 'Invalid notification'}, 400

        # Extract booking ID
        if ref_code.startswith('ZT'):
            booking_id = ref_code[2:].rsplit(
                '-', 1)[0] if '-' in ref_code else ref_code[2:-10]
        else:
            return {'error': 'Invalid reference code'}, 400

        booking = Booking.find_by_id(booking_id)
        if not booking:
            return {'error': 'Booking not found'}, 404

        # Log notification for audit
        print(f"JazzCash notification for booking {booking_id}: {data}")

        return {'message': 'Notification received'}, 200

    except Exception as e:
        return {'error': str(e)}, 500


@payments_bp.route('/status/<booking_id>', methods=['GET'])
@login_required
def get_payment_status(booking_id):
    """Get payment status for a booking"""
    try:
        booking = Booking.find_by_id(booking_id)
        if not booking:
            return {'error': 'Booking not found', 'code': 'NOT_FOUND'}, 404

        # Verify authorization
        if str(booking.customer_id) != str(current_user.id) and str(booking.provider_id) != str(current_user.id):
            return {'error': 'Unauthorized', 'code': 'FORBIDDEN'}, 403

        return {
            'message': 'Payment status retrieved',
            'data': {
                'bookingId': booking_id,
                'paymentStatus': booking.payment_status,
                'paymentMethod': booking.payment_method or 'not_set',
                'paymentTransactionId': booking.payment_transaction_id or 'not_set',
                'totalAmount': booking.total_amount,
                'feedbackId': booking.feedback_id or 'not_provided'
            }
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
