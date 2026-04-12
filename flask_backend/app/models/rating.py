"""Rating model"""

from bson.objectid import ObjectId
from app.models.database import get_ratings_collection
from app.utils.helpers import get_timestamp, is_valid_object_id
from datetime import datetime


class Rating:
    """Rating model for customer reviews of providers"""

    def __init__(self, booking_id, customer_id, provider_id, rating, review=None, **kwargs):
        self._id = kwargs.get('_id')
        self.booking_id = ObjectId(booking_id) if isinstance(
            booking_id, str) else booking_id
        self.customer_id = ObjectId(customer_id) if isinstance(
            customer_id, str) else customer_id
        self.provider_id = ObjectId(provider_id) if isinstance(
            provider_id, str) else provider_id
        self.rating = rating  # 1-5
        self.review = review
        self.created_at = kwargs.get('created_at', get_timestamp())
        self.updated_at = kwargs.get('updated_at', get_timestamp())

    def to_dict(self, include_id=True):
        """Convert to dictionary"""
        data = {
            'bookingId': str(self.booking_id),
            'customerId': str(self.customer_id),
            'providerId': str(self.provider_id),
            'rating': self.rating,
            'review': self.review,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updatedAt': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

        if include_id and self._id:
            data['_id'] = str(self._id)

        return data

    def save(self):
        """Save rating to database"""
        ratings_collection = get_ratings_collection()

        mongo_data = {
            'bookingId': self.booking_id,
            'customerId': self.customer_id,
            'providerId': self.provider_id,
            'rating': self.rating,
            'review': self.review,
            'updatedAt': get_timestamp(),
        }

        if self._id:
            result = ratings_collection.update_one(
                {'_id': self._id},
                {'$set': mongo_data}
            )
            return result.modified_count > 0
        else:
            mongo_data['createdAt'] = get_timestamp()
            result = ratings_collection.insert_one(mongo_data)
            self._id = result.inserted_id
            return True

    @classmethod
    def find_by_id(cls, rating_id):
        """Find rating by ID"""
        if not is_valid_object_id(rating_id):
            return None

        ratings_collection = get_ratings_collection()
        doc = ratings_collection.find_one({'_id': ObjectId(rating_id)})

        if not doc:
            return None

        return cls._from_doc(doc)

    @classmethod
    def find_by_booking(cls, booking_id):
        """Find rating by booking ID"""
        if not is_valid_object_id(booking_id):
            return None

        ratings_collection = get_ratings_collection()
        doc = ratings_collection.find_one({'bookingId': ObjectId(booking_id)})

        if not doc:
            return None

        return cls._from_doc(doc)

    @classmethod
    def find_by_provider(cls, provider_id, skip=0, limit=10):
        """Find all ratings for a provider"""
        if not is_valid_object_id(provider_id):
            return []

        ratings_collection = get_ratings_collection()
        cursor = ratings_collection.find({'providerId': ObjectId(provider_id)}).sort(
            'createdAt', -1).skip(skip).limit(limit)

        ratings = []
        for doc in cursor:
            ratings.append(cls._from_doc(doc))

        return ratings

    @classmethod
    def count_by_provider(cls, provider_id):
        """Count ratings for a provider"""
        if not is_valid_object_id(provider_id):
            return 0

        ratings_collection = get_ratings_collection()
        return ratings_collection.count_documents({'providerId': ObjectId(provider_id)})

    @classmethod
    def get_provider_average_rating(cls, provider_id):
        """Get average rating for a provider"""
        if not is_valid_object_id(provider_id):
            return 0.0

        ratings_collection = get_ratings_collection()

        pipeline = [
            {'$match': {'providerId': ObjectId(provider_id)}},
            {'$group': {
                '_id': None,
                'averageRating': {'$avg': '$rating'},
                'count': {'$sum': 1}
            }}
        ]

        result = list(ratings_collection.aggregate(pipeline))

        if result:
            return result[0]['averageRating'], result[0]['count']

        return 0.0, 0

    @classmethod
    def _from_doc(cls, doc):
        """Create Rating instance from MongoDB document"""
        if not doc:
            return None

        return cls(
            booking_id=doc.get('bookingId'),
            customer_id=doc.get('customerId'),
            provider_id=doc.get('providerId'),
            rating=doc.get('rating'),
            review=doc.get('review'),
            _id=doc.get('_id'),
            created_at=doc.get('createdAt', get_timestamp()),
            updated_at=doc.get('updatedAt', get_timestamp()),
        )
