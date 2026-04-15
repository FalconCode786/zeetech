"""Pakistani Payment Gateway Integration (Easypaisa & Jazzcash)"""

from app.models.booking import Booking
from app.models.feedback import Feedback
from app.utils.errors import ValidationError, NotFoundError, InternalError
from app.utils.helpers import get_timestamp
import requests
import hashlib
import hmac
import json
from typing import Dict, Tuple, Optional
from flask import current_app


class PaymentGateway:
    """Base class for payment gateway integration"""

    @staticmethod
    def requires_feedback(booking_id: str) -> Tuple[bool, Optional[str]]:
        """Check if booking has feedback before payment"""
        feedback = Feedback.find_by_booking(booking_id)
        if not feedback:
            return False, "Feedback is required before payment processing"
        return True, None


class EasyPaisaGateway(PaymentGateway):
    """Easypaisa payment gateway integration"""

    @staticmethod
    def _get_credentials():
        """Get Easypaisa credentials from config"""
        merchant_id = current_app.config.get('EASYPAISA_MERCHANT_ID')
        password = current_app.config.get('EASYPAISA_PASSWORD')
        api_url = current_app.config.get('EASYPAISA_API_URL')

        if not all([merchant_id, password, api_url]):
            raise InternalError('Easypaisa credentials not configured')

        return merchant_id, password, api_url

    @staticmethod
    def _generate_transaction_reference(booking_id: str) -> str:
        """Generate unique transaction reference"""
        return f"BOOK-{booking_id}-{int(get_timestamp().timestamp())}"

    @staticmethod
    def _generate_signature(transaction_ref: str, amount: float, merchant_id: str, password: str) -> str:
        """Generate HMAC signature for Easypaisa"""
        payload = f"{merchant_id}{transaction_ref}{amount}{password}"
        signature = hashlib.sha256(payload.encode()).hexdigest()
        return signature

    @staticmethod
    def create_payment(booking_id: str, phone_number: str) -> Dict:
        """
        Create payment request to Easypaisa

        Args:
            booking_id: Booking ID
            phone_number: Customer mobile number for Easypaisa

        Returns:
            dict: Payment initiation response
        """
        # Check feedback
        has_feedback, error_msg = PaymentGateway.requires_feedback(booking_id)
        if not has_feedback:
            raise ValidationError(error_msg)

        # Get booking
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        if booking.total_amount <= 0:
            raise ValidationError('Booking amount must be greater than 0')

        merchant_id, password, api_url = EasyPaisaGateway._get_credentials()
        transaction_ref = EasyPaisaGateway._generate_transaction_reference(
            booking_id)

        # Generate signature
        signature = EasyPaisaGateway._generate_signature(
            transaction_ref, booking.total_amount, merchant_id, password
        )

        payload = {
            'merchantId': merchant_id,
            'transactionRef': transaction_ref,
            'amount': str(booking.total_amount),
            'phoneNumber': phone_number,
            'storeId': merchant_id,
            'signature': signature,
            'description': f'Service: {booking.subcategory_name}'
        }

        try:
            response = requests.post(
                f'{api_url}/initiate-payment',
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'transactionRef': transaction_ref,
                    'sessionId': data.get('sessionId'),
                    'status': 'pending',
                    'paymentGateway': 'easypaisa'
                }
            else:
                raise InternalError(f'Easypaisa error: {response.text}')

        except requests.RequestException as e:
            raise InternalError(f'Payment gateway connection error: {str(e)}')

    @staticmethod
    def verify_payment(booking_id: str, transaction_ref: str, session_id: str) -> Dict:
        """Verify payment status with Easypaisa"""
        merchant_id, password, api_url = EasyPaisaGateway._get_credentials()

        payload = {
            'merchantId': merchant_id,
            'transactionRef': transaction_ref,
            'sessionId': session_id
        }

        try:
            response = requests.post(
                f'{api_url}/verify-payment',
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    # 'success', 'pending', 'failed'
                    'status': data.get('status'),
                    'transactionId': data.get('transactionId'),
                    'amount': data.get('amount')
                }
            else:
                raise InternalError(f'Verification error: {response.text}')

        except requests.RequestException as e:
            raise InternalError(f'Verification connection error: {str(e)}')


class JazzCashGateway(PaymentGateway):
    """JazzCash payment gateway integration"""

    @staticmethod
    def _get_credentials():
        """Get JazzCash credentials from config"""
        merchant_id = current_app.config.get('JAZZCASH_MERCHANT_ID')
        password = current_app.config.get('JAZZCASH_PASSWORD')
        api_url = current_app.config.get('JAZZCASH_API_URL')

        if not all([merchant_id, password, api_url]):
            raise InternalError('JazzCash credentials not configured')

        return merchant_id, password, api_url

    @staticmethod
    def _generate_reference_code(booking_id: str) -> str:
        """Generate unique reference code for JazzCash"""
        return f"ZT{booking_id}{int(get_timestamp().timestamp())}"[:20]

    @staticmethod
    def _generate_pp_signature(ref_code: str, amount: float, merchant_id: str, password: str) -> str:
        """Generate PP_SIGNATURE for JazzCash"""
        payload = f"{merchant_id}{ref_code}{amount}{password}"
        signature = hashlib.sha256(payload.encode()).hexdigest()
        return signature

    @staticmethod
    def create_payment(booking_id: str, phone_number: str) -> Dict:
        """
        Create payment request to JazzCash

        Args:
            booking_id: Booking ID
            phone_number: Customer mobile number

        Returns:
            dict: Payment initiation response
        """
        # Check feedback
        has_feedback, error_msg = PaymentGateway.requires_feedback(booking_id)
        if not has_feedback:
            raise ValidationError(error_msg)

        # Get booking
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        if booking.total_amount <= 0:
            raise ValidationError('Booking amount must be greater than 0')

        merchant_id, password, api_url = JazzCashGateway._get_credentials()
        ref_code = JazzCashGateway._generate_reference_code(booking_id)

        # Generate signature
        pp_signature = JazzCashGateway._generate_pp_signature(
            ref_code, booking.total_amount, merchant_id, password
        )

        payload = {
            'pp_merchant_id': merchant_id,
            'pp_ref_code': ref_code,
            # Amount in paisa
            'pp_amount': str(int(booking.total_amount * 100)),
            'pp_currency': 'PKR',
            'pp_desc': f'Service: {booking.subcategory_name}',
            'pp_return_url': f"{current_app.config['SERVER_URL']}/api/payments/jazzcash-callback",
            'pp_notify_url': f"{current_app.config['SERVER_URL']}/api/payments/jazzcash-notify",
            'pp_signature': pp_signature
        }

        try:
            # JazzCash redirects to their hosted page, returning URL
            jazzcash_url = f"{api_url}/oauth/authorize"
            payment_url = f"{jazzcash_url}?{'&'.join([f'{k}={v}' for k, v in payload.items(
            )])}"

            return {
                'referenceCode': ref_code,
                'paymentUrl': payment_url,
                'status': 'pending',
                'paymentGateway': 'jazzcash'
            }

        except Exception as e:
            raise InternalError(f'Payment initialization error: {str(e)}')

    @staticmethod
    def verify_payment(ref_code: str) -> Dict:
        """Verify payment status with JazzCash"""
        merchant_id, password, api_url = JazzCashGateway._get_credentials()

        payload = {
            'pp_merchant_id': merchant_id,
            'pp_ref_code': ref_code
        }

        try:
            response = requests.post(
                f'{api_url}/api/verify-transaction',
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'status': data.get('pp_status'),
                    'transactionId': data.get('pp_txnid'),
                    # Convert paisa to rupees
                    'amount': int(data.get('pp_amount', 0)) / 100
                }
            else:
                raise InternalError(f'Verification error: {response.text}')

        except requests.RequestException as e:
            raise InternalError(f'Verification connection error: {str(e)}')


class PaymentService:
    """Service for payment processing with multiple gateways"""

    @staticmethod
    def create_payment(booking_id: str, payment_method: str, phone_number: str = None) -> Dict:
        """
        Create payment with specified gateway

        Args:
            booking_id: Booking ID
            payment_method: 'easypaisa', 'jazzcash', or 'stripe'
            phone_number: Required for Pakistani gateways

        Returns:
            dict: Payment initiation response
        """
        if payment_method == 'easypaisa':
            if not phone_number:
                raise ValidationError('Phone number required for Easypaisa')
            return EasyPaisaGateway.create_payment(booking_id, phone_number)

        elif payment_method == 'jazzcash':
            if not phone_number:
                raise ValidationError('Phone number required for JazzCash')
            return JazzCashGateway.create_payment(booking_id, phone_number)

        elif payment_method == 'stripe':
            from app.services.payment_service_stripe import StripePaymentService
            return StripePaymentService.create_payment_intent(booking_id)

        else:
            raise ValidationError(
                f'Unsupported payment method: {payment_method}')

    @staticmethod
    def confirm_payment(booking_id: str, payment_method: str, transaction_data: Dict) -> Dict:
        """
        Confirm payment and update booking

        Args:
            booking_id: Booking ID
            payment_method: Payment method used
            transaction_data: Transaction verification data

        Returns:
            dict: Payment confirmation status
        """
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        try:
            is_successful = False
            transaction_id = None

            if payment_method == 'easypaisa':
                result = EasyPaisaGateway.verify_payment(
                    booking_id,
                    transaction_data.get('transactionRef'),
                    transaction_data.get('sessionId')
                )
                is_successful = result['status'] == 'success'
                transaction_id = result.get('transactionId')

            elif payment_method == 'jazzcash':
                result = JazzCashGateway.verify_payment(
                    transaction_data.get('referenceCode'))
                is_successful = result['status'] in [
                    'PP056', 'PP000']  # JazzCash success codes
                transaction_id = result.get('transactionId')

            if is_successful:
                # Update booking
                booking.payment_status = 'completed'
                booking.payment_method = payment_method
                booking.payment_transaction_id = transaction_id
                booking.save()

                return {
                    'status': 'success',
                    'message': 'Payment confirmed successfully',
                    'bookingId': booking_id,
                    'transactionId': transaction_id
                }
            else:
                booking.payment_status = 'failed'
                booking.save()
                return {
                    'status': 'failed',
                    'message': 'Payment verification failed'
                }

        except Exception as e:
            raise InternalError(f'Payment confirmation error: {str(e)}')
