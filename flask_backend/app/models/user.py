"""User model"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from app.models.database import get_users_collection
from app.utils.helpers import get_timestamp, is_valid_object_id
from datetime import datetime


class User(UserMixin):
    """User model for authentication and profile management"""

    def __init__(self, email, phone, full_name, role='customer', password=None, **kwargs):
        self._id = kwargs.get('_id')
        self.email = email
        self.phone = phone
        self.full_name = full_name
        self.role = role  # 'customer' or 'provider'
        self.status = kwargs.get('status', 'active')

        # Password
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = kwargs.get('password_hash')

        # Profile information
        self.profile_image = kwargs.get('profile_image')
        self.address = kwargs.get('address')
        self.city = kwargs.get('city')
        self.area = kwargs.get('area')

        # Ratings (for providers)
        self.rating = kwargs.get('rating', 0.0)
        self.total_reviews = kwargs.get('total_reviews', 0)

        # Verification flags
        self.email_verified = kwargs.get('email_verified', False)
        self.phone_verified = kwargs.get('phone_verified', False)

        # Timestamps
        self.created_at = kwargs.get('created_at', get_timestamp())
        self.updated_at = kwargs.get('updated_at', get_timestamp())

    def get_id(self):
        """Get user ID for Flask-Login"""
        return str(self._id)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            '_id': str(self._id),
            'email': self.email,
            'phone': self.phone,
            'fullName': self.full_name,
            'role': self.role,
            'status': self.status,
            'profileImage': self.profile_image,
            'address': self.address,
            'city': self.city,
            'area': self.area,
            'rating': self.rating,
            'totalReviews': self.total_reviews,
            'emailVerified': self.email_verified,
            'phoneVerified': self.phone_verified,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updatedAt': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

        if include_sensitive:
            data['passwordHash'] = self.password_hash

        return data

    def save(self):
        """Save user to database"""
        users_collection = get_users_collection()
        user_data = self.to_dict(include_sensitive=True)
        user_data.pop('_id', None)
        user_data['updated_at'] = get_timestamp()

        # Convert snake_case back to match MongoDB if needed
        mongo_data = {
            'email': self.email,
            'phone': self.phone,
            'fullName': self.full_name,
            'role': self.role,
            'status': self.status,
            'profileImage': self.profile_image,
            'address': self.address,
            'city': self.city,
            'area': self.area,
            'rating': self.rating,
            'totalReviews': self.total_reviews,
            'emailVerified': self.email_verified,
            'phoneVerified': self.phone_verified,
            'passwordHash': self.password_hash,
            'createdAt': self.created_at,
            'updatedAt': get_timestamp(),
        }

        if self._id:
            result = users_collection.update_one(
                {'_id': self._id},
                {'$set': mongo_data}
            )
            return result.modified_count > 0
        else:
            mongo_data['createdAt'] = get_timestamp()
            result = users_collection.insert_one(mongo_data)
            self._id = result.inserted_id
            return True

    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        if not is_valid_object_id(user_id):
            return None

        users_collection = get_users_collection()
        user_doc = users_collection.find_one({'_id': ObjectId(user_id)})

        if not user_doc:
            return None

        return cls._from_doc(user_doc)

    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        users_collection = get_users_collection()
        user_doc = users_collection.find_one({'email': email})

        if not user_doc:
            return None

        return cls._from_doc(user_doc)

    @classmethod
    def find_by_phone(cls, phone):
        """Find user by phone"""
        users_collection = get_users_collection()
        user_doc = users_collection.find_one({'phone': phone})

        if not user_doc:
            return None

        return cls._from_doc(user_doc)

    @classmethod
    def _from_doc(cls, doc):
        """Create User instance from MongoDB document"""
        if not doc:
            return None

        return cls(
            email=doc.get('email'),
            phone=doc.get('phone'),
            full_name=doc.get('fullName'),
            role=doc.get('role', 'customer'),
            _id=doc.get('_id'),
            status=doc.get('status', 'active'),
            password_hash=doc.get('passwordHash'),
            profile_image=doc.get('profileImage'),
            address=doc.get('address'),
            city=doc.get('city'),
            area=doc.get('area'),
            rating=doc.get('rating', 0.0),
            total_reviews=doc.get('totalReviews', 0),
            email_verified=doc.get('emailVerified', False),
            phone_verified=doc.get('phoneVerified', False),
            created_at=doc.get('createdAt', get_timestamp()),
            updated_at=doc.get('updatedAt', get_timestamp()),
        )

    @classmethod
    def create(cls, email, phone, full_name, password, role='customer'):
        """Create and save a new user"""
        # Check if user already exists
        if cls.find_by_email(email):
            return None, 'Email already registered'

        if cls.find_by_phone(phone):
            return None, 'Phone already registered'

        user = cls(email, phone, full_name, role, password)
        if user.save():
            return user, None

        return None, 'Failed to create user'
