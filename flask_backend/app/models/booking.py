"""Booking model"""

from bson.objectid import ObjectId
from app.models.database import get_bookings_collection
from app.utils.helpers import get_timestamp, is_valid_object_id
from datetime import datetime
from enum import Enum


class BookingStatus(Enum):
    """Booking status enumeration"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'


class Booking:
    """Booking model for managing service bookings"""

    def __init__(self, customer_id, subcategory_name, base_amount, preferred_date,
                 preferred_time_slot=None, location=None, **kwargs):
        self._id = kwargs.get('_id')
        self.customer_id = ObjectId(customer_id) if isinstance(
            customer_id, str) else customer_id
        self.provider_id = None

        # Service details
        self.subcategory_name = subcategory_name
        self.base_amount = float(base_amount)
        self.additional_charges = kwargs.get('additional_charges', 0.0)
        self.discount_amount = kwargs.get('discount_amount', 0.0)

        # Booking details
        self.status = kwargs.get('status', BookingStatus.PENDING.value)
        self.problem_description = kwargs.get('problem_description')
        self.special_instructions = kwargs.get('special_instructions')

        # Scheduling
        self.preferred_date = preferred_date
        self.preferred_time_slot = preferred_time_slot

        # Location
        self.location = location or {}

        # Payment
        self.payment_status = kwargs.get(
            'payment_status', PaymentStatus.PENDING.value)
        self.stripe_payment_intent_id = kwargs.get('stripe_payment_intent_id')

        # Rating
        self.customer_rating = kwargs.get('customer_rating')
        self.customer_review = kwargs.get('customer_review')

        # Timestamps
        self.created_at = kwargs.get('created_at', get_timestamp())
        self.updated_at = kwargs.get('updated_at', get_timestamp())
        self.confirmed_at = kwargs.get('confirmed_at')
        self.assigned_at = kwargs.get('assigned_at')
        self.completed_at = kwargs.get('completed_at')

    @property
    def total_amount(self):
        """Calculate total amount"""
        return self.base_amount + self.additional_charges - self.discount_amount

    def set_provider(self, provider_id):
        """Assign provider to booking"""
        self.provider_id = ObjectId(provider_id) if isinstance(
            provider_id, str) else provider_id

    def update_status(self, new_status):
        """Update booking status with validation"""
        current = BookingStatus(self.status)
        target = BookingStatus(new_status)

        # Define valid status transitions
        valid_transitions = {
            BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
            BookingStatus.CONFIRMED: [BookingStatus.ASSIGNED, BookingStatus.CANCELLED],
            BookingStatus.ASSIGNED: [BookingStatus.IN_PROGRESS, BookingStatus.CANCELLED],
            BookingStatus.IN_PROGRESS: [BookingStatus.COMPLETED],
            BookingStatus.COMPLETED: [],  # No transitions from completed
            BookingStatus.CANCELLED: [],  # No transitions from cancelled
        }

        if target not in valid_transitions.get(current, []):
            return False, f'Cannot transition from {current.value} to {target.value}'

        self.status = target.value
        self.updated_at = get_timestamp()

        # Update timestamps for specific transitions
        if target == BookingStatus.CONFIRMED:
            self.confirmed_at = get_timestamp()
        elif target == BookingStatus.ASSIGNED:
            self.assigned_at = get_timestamp()
        elif target == BookingStatus.COMPLETED:
            self.completed_at = get_timestamp()

        return True, None

    def set_rating(self, rating, review=None):
        """Set customer rating and review"""
        if not (1 <= rating <= 5):
            return False, 'Rating must be between 1 and 5'

        if self.status != BookingStatus.COMPLETED.value:
            return False, 'Can only rate completed bookings'

        self.customer_rating = rating
        self.customer_review = review
        self.updated_at = get_timestamp()

        return True, None

    def to_dict(self, include_id=True):
        """Convert to dictionary"""
        data = {
            'customerId': str(self.customer_id),
            'providerId': str(self.provider_id) if self.provider_id else None,
            'subcategoryName': self.subcategory_name,
            'baseAmount': self.base_amount,
            'additionalCharges': self.additional_charges,
            'discountAmount': self.discount_amount,
            'totalAmount': self.total_amount,
            'status': self.status,
            'problemDescription': self.problem_description,
            'specialInstructions': self.special_instructions,
            'preferredDate': self.preferred_date,
            'preferredTimeSlot': self.preferred_time_slot,
            'location': self.location,
            'paymentStatus': self.payment_status,
            'stripePaymentIntentId': self.stripe_payment_intent_id,
            'customerRating': self.customer_rating,
            'customerReview': self.customer_review,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updatedAt': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'confirmedAt': self.confirmed_at.isoformat() if isinstance(self.confirmed_at, datetime) else self.confirmed_at,
            'assignedAt': self.assigned_at.isoformat() if isinstance(self.assigned_at, datetime) else self.assigned_at,
            'completedAt': self.completed_at.isoformat() if isinstance(self.completed_at, datetime) else self.completed_at,
        }

        if include_id and self._id:
            data['_id'] = str(self._id)

        return data

    def save(self):
        """Save booking to database"""
        bookings_collection = get_bookings_collection()

        mongo_data = {
            'customerId': self.customer_id,
            'providerId': self.provider_id,
            'subcategoryName': self.subcategory_name,
            'baseAmount': self.base_amount,
            'additionalCharges': self.additional_charges,
            'discountAmount': self.discount_amount,
            'status': self.status,
            'problemDescription': self.problem_description,
            'specialInstructions': self.special_instructions,
            'preferredDate': self.preferred_date,
            'preferredTimeSlot': self.preferred_time_slot,
            'location': self.location,
            'paymentStatus': self.payment_status,
            'stripePaymentIntentId': self.stripe_payment_intent_id,
            'customerRating': self.customer_rating,
            'customerReview': self.customer_review,
            'updatedAt': get_timestamp(),
            'confirmedAt': self.confirmed_at,
            'assignedAt': self.assigned_at,
            'completedAt': self.completed_at,
        }

        if self._id:
            result = bookings_collection.update_one(
                {'_id': self._id},
                {'$set': mongo_data}
            )
            return result.modified_count > 0
        else:
            mongo_data['createdAt'] = get_timestamp()
            result = bookings_collection.insert_one(mongo_data)
            self._id = result.inserted_id
            return True

    @classmethod
    def find_by_id(cls, booking_id):
        """Find booking by ID"""
        if not is_valid_object_id(booking_id):
            return None

        bookings_collection = get_bookings_collection()
        doc = bookings_collection.find_one({'_id': ObjectId(booking_id)})

        if not doc:
            return None

        return cls._from_doc(doc)

    @classmethod
    def find_by_customer(cls, customer_id, status=None, skip=0, limit=10):
        """Find bookings by customer ID"""
        if not is_valid_object_id(customer_id):
            return []

        bookings_collection = get_bookings_collection()
        query = {'customerId': ObjectId(customer_id)}

        if status:
            query['status'] = status

        cursor = bookings_collection.find(query).sort(
            'createdAt', -1).skip(skip).limit(limit)

        bookings = []
        for doc in cursor:
            bookings.append(cls._from_doc(doc))

        return bookings

    @classmethod
    def count_by_customer(cls, customer_id, status=None):
        """Count bookings by customer"""
        if not is_valid_object_id(customer_id):
            return 0

        bookings_collection = get_bookings_collection()
        query = {'customerId': ObjectId(customer_id)}

        if status:
            query['status'] = status

        return bookings_collection.count_documents(query)

    @classmethod
    def find_all(cls, status=None, skip=0, limit=10):
        """Find all bookings (for admin)"""
        bookings_collection = get_bookings_collection()
        query = {}

        if status:
            query['status'] = status

        cursor = bookings_collection.find(query).sort(
            'createdAt', -1).skip(skip).limit(limit)

        bookings = []
        for doc in cursor:
            bookings.append(cls._from_doc(doc))

        return bookings

    @classmethod
    def count_all(cls, status=None):
        """Count all bookings"""
        bookings_collection = get_bookings_collection()
        query = {}

        if status:
            query['status'] = status

        return bookings_collection.count_documents(query)

    @classmethod
    def _from_doc(cls, doc):
        """Create Booking instance from MongoDB document"""
        if not doc:
            return None

        booking = cls(
            customer_id=doc.get('customerId'),
            subcategory_name=doc.get('subcategoryName'),
            base_amount=doc.get('baseAmount'),
            preferred_date=doc.get('preferredDate'),
            _id=doc.get('_id'),
            status=doc.get('status', BookingStatus.PENDING.value),
            problem_description=doc.get('problemDescription'),
            special_instructions=doc.get('specialInstructions'),
            preferred_time_slot=doc.get('preferredTimeSlot'),
            location=doc.get('location', {}),
            payment_status=doc.get(
                'paymentStatus', PaymentStatus.PENDING.value),
            stripe_payment_intent_id=doc.get('stripePaymentIntentId'),
            additional_charges=doc.get('additionalCharges', 0.0),
            discount_amount=doc.get('discountAmount', 0.0),
            customer_rating=doc.get('customerRating'),
            customer_review=doc.get('customerReview'),
            created_at=doc.get('createdAt', get_timestamp()),
            updated_at=doc.get('updatedAt', get_timestamp()),
            confirmed_at=doc.get('confirmedAt'),
            assigned_at=doc.get('assignedAt'),
            completed_at=doc.get('completedAt'),
        )

        booking.provider_id = doc.get('providerId')

        return booking
