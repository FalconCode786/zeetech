"""Feedback model"""

from app.models.database import get_feedbacks_collection
from app.utils.helpers import get_timestamp
from datetime import datetime
from typing import Optional


class Feedback:
    """Feedback model for collecting user feedback before payment"""

    def __init__(self, booking_id: str, customer_id: str, rating: int, comment: str = "", **kwargs):
        self.id = kwargs.get('id')
        self.booking_id = booking_id
        self.customer_id = customer_id
        self.rating = rating  # 1-5 stars
        self.comment = comment
        self.created_at = kwargs.get('created_at', get_timestamp())
        self.updated_at = kwargs.get('updated_at', get_timestamp())

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate feedback data"""
        if not self.booking_id:
            return False, "Booking ID is required"
        if not self.customer_id:
            return False, "Customer ID is required"
        if not isinstance(self.rating, int) or not (1 <= self.rating <= 5):
            return False, "Rating must be an integer between 1 and 5"
        if len(self.comment) > 1000:
            return False, "Comment must be less than 1000 characters"
        return True, None

    def to_dict(self, include_id: bool = True) -> dict:
        """Convert to dictionary"""
        data = {
            'bookingId': self.booking_id,
            'customerId': self.customer_id,
            'rating': self.rating,
            'comment': self.comment,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updatedAt': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

        if include_id and self.id:
            data['id'] = self.id

        return data

    def save(self) -> bool:
        """Save feedback to database"""
        is_valid, error_msg = self.validate()
        if not is_valid:
            print(f"Validation error: {error_msg}")
            return False

        feedbacks_collection = get_feedbacks_collection()
        supabase_data = {
            'bookingId': self.booking_id,
            'customerId': self.customer_id,
            'rating': self.rating,
            'comment': self.comment,
            'updatedAt': get_timestamp(),
        }

        try:
            if self.id:
                result = feedbacks_collection.update(
                    supabase_data).eq('id', self.id).execute()
                return len(result.data) > 0
            else:
                supabase_data['createdAt'] = self.created_at
                result = feedbacks_collection.insert(supabase_data).execute()
                if result.data:
                    self.id = result.data[0]['id']
                    return True
                return False
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False

    @classmethod
    def find_by_id(cls, feedback_id: str) -> Optional['Feedback']:
        """Find feedback by ID"""
        if not feedback_id:
            return None

        feedbacks_collection = get_feedbacks_collection()
        try:
            response = feedbacks_collection.select(
                '*').eq('id', feedback_id).execute()
            if response.data:
                return cls._from_doc(response.data[0])
        except Exception as e:
            print(f"Error finding feedback: {e}")
        return None

    @classmethod
    def find_by_booking(cls, booking_id: str) -> Optional['Feedback']:
        """Find feedback for a specific booking"""
        if not booking_id:
            return None

        feedbacks_collection = get_feedbacks_collection()
        try:
            response = feedbacks_collection.select(
                '*').eq('bookingId', booking_id).execute()
            if response.data:
                return cls._from_doc(response.data[0])
        except Exception as e:
            print(f"Error finding feedback: {e}")
        return None

    @classmethod
    def find_by_customer(cls, customer_id: str, skip: int = 0, limit: int = 10) -> list['Feedback']:
        """Find feedbacks from a customer"""
        feedbacks = []
        try:
            response = get_feedbacks_collection().select('*')\
                .eq('customerId', customer_id)\
                .order('createdAt', desc=True)\
                .range(skip, skip + limit - 1).execute()
            for doc in response.data:
                feedbacks.append(cls._from_doc(doc))
        except Exception as e:
            print(f"Error finding feedbacks: {e}")
        return feedbacks

    @classmethod
    def _from_doc(cls, doc: dict) -> Optional['Feedback']:
        """Create Feedback instance from Supabase record"""
        if not doc:
            return None

        feedback = cls(
            booking_id=doc.get('bookingId'),
            customer_id=doc.get('customerId'),
            rating=doc.get('rating'),
            comment=doc.get('comment', ''),
            id=doc.get('id'),
            created_at=doc.get('createdAt'),
            updated_at=doc.get('updatedAt'),
        )
        return feedback
