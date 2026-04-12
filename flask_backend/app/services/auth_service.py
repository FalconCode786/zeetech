"""Authentication service with business logic"""

from app.models.user import User
from app.utils.errors import ValidationError, ConflictError, UnauthorizedError
from app.utils.helpers import validate_email, validate_phone


class AuthService:
    """Service class for authentication operations"""

    @staticmethod
    def register(email, phone, full_name, password, role='customer'):
        """
        Register a new user

        Args:
            email: User email
            phone: User phone number
            full_name: User full name
            password: User password (will be hashed)
            role: User role (customer or provider)

        Returns:
            tuple: (user, error_message)
        """
        # Validation
        if not email or not email.strip():
            raise ValidationError('Email is required')

        if not validate_email(email):
            raise ValidationError('Invalid email format')

        if not phone or not phone.strip():
            raise ValidationError('Phone is required')

        if not validate_phone(phone):
            raise ValidationError('Invalid phone format')

        if not full_name or not full_name.strip():
            raise ValidationError('Full name is required')

        if not password or len(password) < 6:
            raise ValidationError('Password must be at least 6 characters')

        if role not in ['customer', 'provider']:
            raise ValidationError('Role must be either customer or provider')

        # Check if user already exists
        if User.find_by_email(email):
            raise ConflictError('Email already registered')

        if User.find_by_phone(phone):
            raise ConflictError('Phone already registered')

        # Create user
        user = User(email, phone, full_name, role, password)
        if user.save():
            return user

        raise Exception('Failed to create user')

    @staticmethod
    def login(email_or_phone, password):
        """
        Login user with email or phone

        Args:
            email_or_phone: User email or phone
            password: User password

        Returns:
            User: Authenticated user instance
        """
        if not email_or_phone or not password:
            raise ValidationError('Email/Phone and password are required')

        # Try to find user by email first
        user = User.find_by_email(email_or_phone)

        # If not found, try phone
        if not user:
            user = User.find_by_phone(email_or_phone)

        if not user:
            raise UnauthorizedError('Invalid email/phone or password')

        if not user.check_password(password):
            raise UnauthorizedError('Invalid email/phone or password')

        if user.status != 'active':
            raise UnauthorizedError('User account is not active')

        return user

    @staticmethod
    def update_profile(user, data):
        """
        Update user profile

        Args:
            user: User instance
            data: Dictionary with fields to update

        Returns:
            User: Updated user instance
        """
        # Update allowed fields
        allowed_fields = ['fullName', 'phone',
                          'address', 'city', 'area', 'profileImage']

        for field, value in data.items():
            if field not in allowed_fields:
                continue

            # Convert camelCase to snake_case for internal use
            if field == 'fullName':
                if value and value.strip():
                    user.full_name = value.strip()
            elif field == 'phone':
                if value and value.strip():
                    # Check if phone is already used by another user
                    existing = User.find_by_phone(value.strip())
                    if existing and existing.get_id() != user.get_id():
                        raise ConflictError('Phone number already in use')

                    if not validate_phone(value.strip()):
                        raise ValidationError('Invalid phone format')

                    user.phone = value.strip()
            elif field == 'address':
                user.address = value
            elif field == 'city':
                user.city = value
            elif field == 'area':
                user.area = value
            elif field == 'profileImage':
                user.profile_image = value

        if user.save():
            return user

        raise Exception('Failed to update profile')

    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password

        Args:
            user: User instance
            old_password: Current password
            new_password: New password

        Returns:
            bool: Success status
        """
        if not old_password or not new_password:
            raise ValidationError('Old and new passwords are required')

        if not user.check_password(old_password):
            raise UnauthorizedError('Current password is incorrect')

        if len(new_password) < 6:
            raise ValidationError('New password must be at least 6 characters')

        user.set_password(new_password)
        if user.save():
            return True

        raise Exception('Failed to change password')

    @staticmethod
    def verify_email(user):
        """Mark email as verified"""
        user.email_verified = True
        if user.save():
            return True
        raise Exception('Failed to verify email')

    @staticmethod
    def verify_phone(user):
        """Mark phone as verified"""
        user.phone_verified = True
        if user.save():
            return True
        raise Exception('Failed to verify phone')
