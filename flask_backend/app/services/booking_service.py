"""Booking management business logic"""

from app.models.booking import Booking, BookingStatus, PaymentStatus
from app.models.service import ServiceCategory
from app.models.user import User
from app.utils.errors import ValidationError, NotFoundError, ConflictError
from datetime import datetime


class BookingService:
    """Service for managing bookings"""

    @staticmethod
    def create_booking(customer_id, data):
        """
        Create a new booking

        Args:
            customer_id: Customer user ID
            data: Dictionary with booking data

        Returns:
            Booking: Created booking
        """
        # Validate required fields
        subcategory_name = data.get('subcategoryName')
        if not subcategory_name:
            raise ValidationError('Subcategory name is required')

        base_amount = data.get('baseAmount')
        if not base_amount or float(base_amount) <= 0:
            raise ValidationError('Valid base amount is required')

        preferred_date = data.get('preferredDate')
        if not preferred_date:
            raise ValidationError('Preferred date is required')

        # Validate category exists by searching for subcategory
        subcategory_found = False
        categories, _ = BookingService._search_subcategory(subcategory_name)
        if not categories:
            raise NotFoundError('Service category not found')

        # Create booking
        booking = Booking(
            customer_id=customer_id,
            subcategory_name=subcategory_name,
            base_amount=base_amount,
            preferred_date=preferred_date,
            preferred_time_slot=data.get('preferredTimeSlot'),
            location=data.get('location'),
            problem_description=data.get('problemDescription'),
            special_instructions=data.get('specialInstructions'),
            additional_charges=float(data.get('additionalCharges', 0)),
            discount_amount=float(data.get('discountAmount', 0)),
        )

        if booking.save():
            return booking

        raise Exception('Failed to create booking')

    @staticmethod
    def _search_subcategory(name):
        """Search for a subcategory across all categories"""
        from app.models.database import supabase_client

        try:
            # Get all service categories and filter by subcategory name
            response = supabase_client.table(
                'serviceCategories').select('*').execute()

            results = []
            if response.data:
                for category in response.data:
                    subcategories = category.get('subcategories', [])
                    filtered_subs = [
                        s for s in subcategories if s.get('name') == name]
                    if filtered_subs:
                        results.append({
                            'id': category.get('id'),
                            'subcategories': filtered_subs
                        })

            return results, len(results)
        except Exception as e:
            print(f"Error searching subcategory: {e}")
            return [], 0

    @staticmethod
    def get_booking(booking_id):
        """
        Get a booking by ID

        Args:
            booking_id: Booking ID

        Returns:
            Booking: Booking instance
        """
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        return booking

    @staticmethod
    def list_customer_bookings(customer_id, status=None, skip=0, limit=10):
        """
        List bookings for a customer

        Args:
            customer_id: Customer ID
            status: Filter by status (optional)
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            tuple: (bookings list, total count)
        """
        bookings = Booking.find_by_customer(
            customer_id, status=status, skip=skip, limit=limit)
        total = Booking.count_by_customer(customer_id, status=status)

        return bookings, total

    @staticmethod
    def update_booking_status(booking_id, new_status):
        """
        Update booking status

        Args:
            booking_id: Booking ID
            new_status: New status value

        Returns:
            Booking: Updated booking
        """
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        # Validate status value
        valid_statuses = [s.value for s in BookingStatus]
        if new_status not in valid_statuses:
            raise ValidationError(
                f'Invalid status. Must be one of: {", ".join(valid_statuses)}')

        # Update status with validation
        success, error = booking.update_status(new_status)
        if not success:
            raise ValidationError(error)

        if booking.save():
            return booking

        raise Exception('Failed to update booking status')

    @staticmethod
    def assign_provider(booking_id, provider_id):
        """
        Assign a provider to a booking

        Args:
            booking_id: Booking ID
            provider_id: Provider user ID

        Returns:
            Booking: Updated booking
        """
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        # Verify provider exists and is a provider
        provider = User.find_by_id(provider_id)
        if not provider:
            raise NotFoundError('Provider not found')

        if provider.role != 'provider':
            raise ValidationError('User is not a provider')

        booking.set_provider(provider_id)

        if booking.save():
            return booking

        raise Exception('Failed to assign provider')

    @staticmethod
    def update_additional_charges(booking_id, additional_charges):
        """
        Update additional charges for a booking

        Args:
            booking_id: Booking ID
            additional_charges: Additional charges amount

        Returns:
            Booking: Updated booking
        """
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        booking.additional_charges = float(additional_charges)

        if booking.save():
            return booking

        raise Exception('Failed to update charges')

    @staticmethod
    def apply_discount(booking_id, discount_amount):
        """
        Apply discount to a booking

        Args:
            booking_id: Booking ID
            discount_amount: Discount amount

        Returns:
            Booking: Updated booking
        """
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        booking.discount_amount = float(discount_amount)

        if booking.save():
            return booking

        raise Exception('Failed to apply discount')

    @staticmethod
    def update_payment_status(booking_id, payment_status):
        """
        Update payment status for a booking

        Args:
            booking_id: Booking ID
            payment_status: New payment status

        Returns:
            Booking: Updated booking
        """
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        # Validate payment status
        valid_statuses = [s.value for s in PaymentStatus]
        if payment_status not in valid_statuses:
            raise ValidationError(
                f'Invalid payment status. Must be one of: {", ".join(valid_statuses)}')

        booking.payment_status = payment_status

        if booking.save():
            return booking

        raise Exception('Failed to update payment status')

    @staticmethod
    def set_stripe_payment_intent(booking_id, intent_id):
        """
        Set Stripe payment intent ID for a booking

        Args:
            booking_id: Booking ID
            intent_id: Stripe payment intent ID

        Returns:
            Booking: Updated booking
        """
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        booking.stripe_payment_intent_id = intent_id

        if booking.save():
            return booking

        raise Exception('Failed to set payment intent')
