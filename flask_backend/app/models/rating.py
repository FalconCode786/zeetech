"""Rating model"""

from app.models.database import get_ratings_collection
from app.utils.helpers import get_timestamp, is_valid_object_id
from datetime import datetime


class Rating:
    """Rating model for customer reviews of providers"""

    def __init__(self, booking_id, customer_id, provider_id, rating, review=None, **kwargs):
        self.id = kwargs.get('id')
        self.booking_id = str(booking_id) if booking_id else None
        self.customer_id = str(customer_id) if customer_id else None
        self.provider_id = str(provider_id) if provider_id else None
        self.rating = rating  # 1-5
        self.review = review
        self.created_at = kwargs.get('created_at', get_timestamp())
        self.updated_at = kwargs.get('updated_at', get_timestamp())

    def to_dict(self, include_id=True):
        """Convert to dictionary"""
        data = {
            'bookingId': self.booking_id,
            'customerId': self.customer_id,
            'providerId': self.provider_id,
            'rating': self.rating,
            'review': self.review,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }

        if include_id and self.id:
            data['id'] = self.id

        return data

    def save(self):
        """Save rating to database via Supabase"""
        from app.models.database import get_db

        supabase_client = get_db()
        data = {
            'bookingId': self.booking_id,
            'customerId': self.customer_id,
            'providerId': self.provider_id,
            'rating': self.rating,
            'review': self.review,
        }

        if self.id:
            # Update existing rating
            response = supabase_client.table('ratings').update(
                data).eq('id', self.id).execute()
            return response.data is not None
        else:
            # Insert new rating
            data['createdAt'] = self.created_at
            response = supabase_client.table('ratings').insert(data).execute()
            if response.data:
                self.id = response.data[0]['id']
                return True
            return False

    @classmethod
    def find_by_id(cls, rating_id):
        """Find rating by ID"""
        from app.models.database import get_db

        supabase_client = get_db()
        try:
            response = supabase_client.table('ratings').select(
                '*').eq('id', int(rating_id)).execute()
            if response.data and len(response.data) > 0:
                doc = response.data[0]
                return cls._from_doc(doc)
            return None
        except Exception:
            return None

    @classmethod
    def find_by_booking(cls, booking_id):
        """Find rating by booking ID"""
        from app.models.database import get_db

        supabase_client = get_db()
        try:
            response = supabase_client.table('ratings').select(
                '*').eq('bookingId', str(booking_id)).execute()
            if response.data and len(response.data) > 0:
                doc = response.data[0]
                return cls._from_doc(doc)
            return None
        except Exception:
            return None

    @classmethod
    def find_by_provider(cls, provider_id, skip=0, limit=10):
        """Find all ratings for a provider"""
        from app.models.database import supabase_client

        try:
            start = skip
            end = skip + limit - 1
            response = supabase_client.table('ratings').select(
                '*').eq('providerId', str(provider_id)).order('createdAt', desc=True).range(start, end).execute()

            ratings = []
            if response.data:
                for doc in response.data:
                    ratings.append(cls._from_doc(doc))
            return ratings
        except Exception:
            return []

    @classmethod
    def count_by_provider(cls, provider_id):
        """Count ratings for a provider"""
        from app.models.database import supabase_client

        try:
            response = supabase_client.table('ratings').select(
                'id', count='exact').eq('providerId', str(provider_id)).execute()
            return response.count if response.count else 0
        except Exception:
            return 0

    @classmethod
    def get_provider_average_rating(cls, provider_id):
        """Get average rating for a provider"""
        from app.models.database import supabase_client

        try:
            response = supabase_client.table('ratings').select(
                'rating').eq('providerId', str(provider_id)).execute()
            if response.data and len(response.data) > 0:
                ratings = [r['rating'] for r in response.data]
                avg = sum(ratings) / len(ratings)
                return avg, len(ratings)
            return 0.0, 0
        except Exception:
            return 0.0, 0

    @classmethod
    def _from_doc(cls, doc):
        """Create Rating instance from Supabase record"""
        if not doc:
            return None

        return cls(
            booking_id=doc.get('bookingId'),
            customer_id=doc.get('customerId'),
            provider_id=doc.get('providerId'),
            rating=doc.get('rating'),
            review=doc.get('review'),
            id=doc.get('id'),
            created_at=doc.get('createdAt', get_timestamp()),
            updated_at=doc.get('updatedAt', get_timestamp()),
        )
