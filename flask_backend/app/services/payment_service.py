"""Payment processing with Stripe integration"""

from app.models.booking import Booking
from app.utils.errors import ValidationError, NotFoundError, InternalError
import stripe
import os


class PaymentService:
    """Service for payment processing with Stripe"""

    @staticmethod
    def initialize():
        """Initialize Stripe API"""
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe.api_key:
            raise RuntimeError('STRIPE_SECRET_KEY not configured')

    @staticmethod
    def create_payment_intent(booking_id, currency='usd'):
        """
        Create a Stripe payment intent for a booking

        Args:
            booking_id: Booking ID
            currency: Currency code (default: usd)

        Returns:
            dict: Payment intent details
        """
        PaymentService.initialize()

        # Get booking
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        if booking.total_amount <= 0:
            raise ValidationError('Booking amount must be greater than 0')

        try:
            # Create payment intent
            amount_in_cents = int(booking.total_amount * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency=currency,
                description=f'Booking {booking_id} for service {booking.subcategory_name}',
                metadata={
                    'booking_id': str(booking_id),
                    'customer_id': str(booking.customer_id),
                    'provider_id': str(booking.provider_id) if booking.provider_id else 'unassigned'
                }
            )

            # Save intent ID to booking
            from app.services.booking_service import BookingService
            BookingService.set_stripe_payment_intent(
                str(booking_id), intent.id)

            return {
                'clientSecret': intent.client_secret,
                'paymentIntentId': intent.id,
                'amount': booking.total_amount,
                'currency': currency,
                'status': intent.status
            }

        except stripe.error.StripeError as e:
            raise InternalError(f'Stripe error: {str(e)}')
        except Exception as e:
            raise InternalError(f'Payment error: {str(e)}')

    @staticmethod
    def confirm_payment(booking_id, payment_intent_id):
        """
        Confirm a payment for a booking

        Args:
            booking_id: Booking ID
            payment_intent_id: Stripe payment intent ID

        Returns:
            dict: Payment confirmation details
        """
        PaymentService.initialize()

        # Get booking
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        try:
            # Retrieve payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == 'succeeded':
                # Update booking payment status
                from app.services.booking_service import BookingService
                BookingService.update_payment_status(
                    str(booking_id), 'completed')

                return {
                    'success': True,
                    'message': 'Payment confirmed successfully',
                    'paymentIntentId': intent.id,
                    'status': intent.status,
                    'chargeId': intent.charges.data[0].id if intent.charges.data else None
                }
            elif intent.status == 'processing':
                return {
                    'success': False,
                    'message': 'Payment is still processing',
                    'status': intent.status
                }
            else:
                return {
                    'success': False,
                    'message': f'Payment failed: {intent.status}',
                    'status': intent.status
                }

        except stripe.error.StripeError as e:
            raise InternalError(f'Stripe error: {str(e)}')
        except Exception as e:
            raise InternalError(f'Payment confirmation error: {str(e)}')

    @staticmethod
    def handle_webhook(event):
        """
        Handle Stripe webhook events

        Args:
            event: Stripe event object

        Returns:
            bool: Success status
        """
        PaymentService.initialize()

        try:
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                booking_id = payment_intent['metadata'].get('booking_id')

                if booking_id:
                    from app.services.booking_service import BookingService
                    BookingService.update_payment_status(
                        booking_id, 'completed')

                return True

            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                booking_id = payment_intent['metadata'].get('booking_id')

                if booking_id:
                    from app.services.booking_service import BookingService
                    BookingService.update_payment_status(booking_id, 'failed')

                return True

            elif event['type'] == 'charge.refunded':
                charge = event['data']['object']
                # Find booking by payment intent
                if 'payment_intent' in charge and charge['payment_intent']:
                    # Update booking payment status to refunded
                    return True

            return True

        except Exception as e:
            raise InternalError(f'Webhook handling error: {str(e)}')

    @staticmethod
    def refund_payment(payment_intent_id, amount=None):
        """
        Refund a payment

        Args:
            payment_intent_id: Stripe payment intent ID
            amount: Amount to refund (if None, full refund)

        Returns:
            dict: Refund details
        """
        PaymentService.initialize()

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if not intent.charges.data:
                raise ValidationError(
                    'No charges found for this payment intent')

            charge = intent.charges.data[0]

            # Refund the charge
            refund_kwargs = {'charge': charge.id}

            if amount:
                refund_kwargs['amount'] = int(amount * 100)

            refund = stripe.Refund.create(**refund_kwargs)

            return {
                'success': True,
                'refundId': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status,
                'chargeId': charge.id
            }

        except stripe.error.StripeError as e:
            raise InternalError(f'Stripe error: {str(e)}')
        except Exception as e:
            raise InternalError(f'Refund error: {str(e)}')
