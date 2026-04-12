"""Payment processing routes"""

from flask import Blueprint, request
from flask_login import login_required
from app.services.payment_service import PaymentService
from app.services.booking_service import BookingService
from app.utils.decorators import admin_required
from app.utils.errors import AppError
from app.utils.helpers import serialize_document, is_valid_object_id
import hmac
import hashlib
import json
import os

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@payments_bp.route('/create-intent', methods=['POST'])
@login_required
def create_payment_intent():
    """Create a Stripe payment intent for a booking"""
    try:
        data = request.get_json()

        if not data or 'bookingId' not in data:
            return {'error': 'Booking ID is required', 'code': 'INVALID_REQUEST'}, 400

        booking_id = data['bookingId']

        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        currency = data.get('currency', 'usd')

        payment_info = PaymentService.create_payment_intent(
            booking_id, currency)

        return {
            'message': 'Payment intent created successfully',
            'data': payment_info
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@payments_bp.route('/confirm', methods=['POST'])
@login_required
def confirm_payment():
    """Confirm a payment"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        booking_id = data.get('bookingId')
        payment_intent_id = data.get('paymentIntentId')

        if not booking_id or not payment_intent_id:
            return {'error': 'Booking ID and payment intent ID are required', 'code': 'INVALID_REQUEST'}, 400

        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        result = PaymentService.confirm_payment(booking_id, payment_intent_id)

        return {
            'message': 'Payment confirmation processed',
            'data': result
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@payments_bp.route('/refund', methods=['POST'])
@admin_required
def refund_payment():
    """Refund a payment (admin only)"""
    try:
        data = request.get_json()

        if not data or 'paymentIntentId' not in data:
            return {'error': 'Payment intent ID is required', 'code': 'INVALID_REQUEST'}, 400

        payment_intent_id = data['paymentIntentId']
        amount = data.get('amount')

        result = PaymentService.refund_payment(payment_intent_id, amount)

        return {
            'message': 'Payment refunded successfully',
            'data': result
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@payments_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle Stripe webhook"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')

        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

        if not webhook_secret:
            return {'error': 'Webhook secret not configured', 'code': 'CONFIG_ERROR'}, 500

        try:
            # Verify webhook signature
            import stripe
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            return {'error': 'Invalid payload', 'code': 'INVALID_PAYLOAD'}, 400
        except Exception as e:
            return {'error': f'Webhook error: {str(e)}', 'code': 'WEBHOOK_ERROR'}, 400

        # Handle the event
        PaymentService.handle_webhook(event)

        return {'status': 'success'}, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
