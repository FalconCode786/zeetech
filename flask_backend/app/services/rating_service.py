"""Rating and review business logic"""

from app.models.rating import Rating
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.utils.errors import ValidationError, NotFoundError, ConflictError


class RatingService:
    """Service for managing ratings and reviews"""

    @staticmethod
    def create_rating(booking_id, customer_id, rating, review=None):
        """
        Create a rating for a completed booking

        Args:
            booking_id: Booking ID
            customer_id: Customer ID (who is rating)
            rating: Rating value (1-5)
            review: Review text (optional)

        Returns:
            Rating: Created rating
        """
        # Validate rating value
        try:
            rating_value = int(rating)
            if not (1 <= rating_value <= 5):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError('Rating must be an integer between 1 and 5')

        # Get booking
        booking = Booking.find_by_id(booking_id)
        if not booking:
            raise NotFoundError('Booking not found')

        # Verify customer is the one who created the booking
        if str(booking.customer_id) != customer_id:
            raise ValidationError('Only the customer can rate this booking')

        # Verify booking is completed
        if booking.status != BookingStatus.COMPLETED.value:
            raise ValidationError('Can only rate completed bookings')

        # Check if rating already exists
        existing = Rating.find_by_booking(booking_id)
        if existing:
            raise ConflictError('Booking has already been rated')

        # Get provider
        provider_id = booking.provider_id
        if not provider_id:
            raise ValidationError('Booking does not have an assigned provider')

        provider = User.find_by_id(str(provider_id))
        if not provider:
            raise NotFoundError('Provider not found')

        # Create rating
        rating_obj = Rating(
            booking_id=booking_id,
            customer_id=customer_id,
            provider_id=provider_id,
            rating=rating_value,
            review=review
        )

        if rating_obj.save():
            # Update provider's aggregate rating
            RatingService._update_provider_rating(str(provider_id))

            # Update booking with rating
            booking.customer_rating = rating_value
            booking.customer_review = review
            booking.save()

            return rating_obj

        raise Exception('Failed to create rating')

    @staticmethod
    def _update_provider_rating(provider_id):
        """
        Update provider's average rating

        Args:
            provider_id: Provider user ID
        """
        avg_rating, count = Rating.get_provider_average_rating(provider_id)

        provider = User.find_by_id(provider_id)
        if provider:
            provider.rating = round(avg_rating, 2)
            provider.total_reviews = count
            provider.save()

    @staticmethod
    def get_rating(rating_id):
        """
        Get a rating by ID

        Args:
            rating_id: Rating ID

        Returns:
            Rating: Rating instance
        """
        rating = Rating.find_by_id(rating_id)
        if not rating:
            raise NotFoundError('Rating not found')

        return rating

    @staticmethod
    def get_booking_rating(booking_id):
        """
        Get rating for a specific booking

        Args:
            booking_id: Booking ID

        Returns:
            Rating: Rating instance or None
        """
        return Rating.find_by_booking(booking_id)

    @staticmethod
    def get_provider_ratings(provider_id, skip=0, limit=10):
        """
        Get all ratings for a provider

        Args:
            provider_id: Provider user ID
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            tuple: (ratings list, total count, average rating)
        """
        ratings = Rating.find_by_provider(provider_id, skip=skip, limit=limit)
        total = Rating.count_by_provider(provider_id)
        avg_rating, _ = Rating.get_provider_average_rating(provider_id)

        return ratings, total, avg_rating

    @staticmethod
    def update_rating(rating_id, data):
        """
        Update a rating (only review text can be updated)

        Args:
            rating_id: Rating ID
            data: Data to update

        Returns:
            Rating: Updated rating
        """
        rating = Rating.find_by_id(rating_id)
        if not rating:
            raise NotFoundError('Rating not found')

        # Only allow updating review text
        if 'review' in data:
            rating.review = data['review']

            if rating.save():
                return rating

            raise Exception('Failed to update rating')

        return rating

    @staticmethod
    def get_provider_stats(provider_id):
        """
        Get rating statistics for a provider

        Args:
            provider_id: Provider user ID

        Returns:
            dict: Rating statistics
        """
        avg_rating, total = Rating.get_provider_average_rating(provider_id)

        return {
            'averageRating': round(avg_rating, 2),
            'totalRatings': total
        }
