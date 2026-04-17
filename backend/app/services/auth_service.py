"""Authentication service."""
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from app.utils.supabase_client import get_supabase
from app.utils.helpers import (
    is_valid_email, is_valid_phone, is_valid_password,
    normalize_phone
)
from app.config import Config


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def register(email: str, phone: str, fullName: str, password: str, role: str = 'customer') -> dict:
        """Register a new user."""
        try:
            # Normalize inputs
            email = email.lower().strip()
            phone = normalize_phone(phone)

            # Validate inputs
            if not is_valid_email(email):
                raise ValueError('Valid email is required')

            if not is_valid_phone(phone):
                raise ValueError('Valid phone number is required')

            if not fullName or len(fullName) < 2:
                raise ValueError('Full name is required')

            if not is_valid_password(password):
                raise ValueError(
                    'Password must be at least 8 characters with uppercase, lowercase, digit, and special character')

            if role not in ['customer', 'provider']:
                raise ValueError('Role must be customer or provider')

            provider_phone = normalize_phone(Config.PROVIDER_LOGIN_PHONE)
            if email == Config.PROVIDER_LOGIN_EMAIL or phone == provider_phone:
                raise ValueError(
                    'This email/phone is reserved for provider login')

            # Get Supabase client
            supabase = get_supabase()

            # Check if email already exists
            try:
                existing_email = supabase.table('users').select(
                    'id').eq('email', email).maybe_single().execute()
                if existing_email and hasattr(existing_email, 'data') and existing_email.data:
                    raise ValueError('Email already registered')
            except Exception as e:
                print(f'[Auth] Email check error: {str(e)}')

            # Check if phone already exists
            try:
                existing_phone = supabase.table('users').select(
                    'id').eq('phone', phone).maybe_single().execute()
                if existing_phone and hasattr(existing_phone, 'data') and existing_phone.data:
                    raise ValueError('Phone number already registered')
            except Exception as e:
                print(f'[Auth] Phone check error: {str(e)}')

            # Hash password
            hashed_password = bcrypt.hashpw(password.encode(
                'utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Create user
            user_id = str(uuid.uuid4())

            user_data = {
                'id': user_id,
                'email': email,
                'phone': phone,
                'fullName': fullName,
                'role': role,
                'password': hashed_password,
                'status': 'active',
            }

            result = supabase.table('users').insert(user_data).execute()

            if not result or not hasattr(result, 'data') or not result.data:
                print(f'[Auth] Insert failed. Response: {result}')
            # Generate token
            token = AuthService._generate_token(user_id, role)

            return {
                'user': AuthService._format_user(result.data[0]),
                'token': token
            }

        except Exception as e:
            print(f'[Auth] Register error: {str(e)}')
            raise

    @staticmethod
    def login(email_or_phone: str, password: str) -> dict:
        """Login a user."""
        try:
            supabase = get_supabase()

            normalized_input = (email_or_phone or '').strip()
            provider_phone = normalize_phone(Config.PROVIDER_LOGIN_PHONE)
            if (
                normalized_input.lower() == Config.PROVIDER_LOGIN_EMAIL.lower()
                or normalize_phone(normalized_input) == provider_phone
            ):
                if password != Config.PROVIDER_LOGIN_PASSWORD:
                    raise ValueError('Invalid email/phone or password')

                provider_user = AuthService._ensure_constant_provider_account(
                    supabase)
                token = AuthService._generate_token(
                    provider_user['id'], provider_user['role'])
                return {
                    'user': AuthService._format_user(provider_user),
                    'token': token
                }

            # Find user
            user = None
            if is_valid_email(email_or_phone):
                result = supabase.table('users').select(
                    '*').eq('email', email_or_phone.lower()).maybe_single().execute()
                user = result.data if result and hasattr(
                    result, 'data') else None
            elif is_valid_phone(email_or_phone):
                normalized_phone = normalize_phone(email_or_phone)
                result = supabase.table('users').select(
                    '*').eq('phone', normalized_phone).maybe_single().execute()
                user = result.data if result and hasattr(
                    result, 'data') else None

            if not user:
                raise ValueError('Invalid email/phone or password')

            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                raise ValueError('Invalid email/phone or password')

            # Generate token
            token = AuthService._generate_token(user['id'], user['role'])

            return {
                'user': AuthService._format_user(user),
                'token': token
            }

        except Exception as e:
            print(f'[Auth] Login error: {str(e)}')
            raise

    @staticmethod
    def _generate_token(user_id: str, role: str) -> str:
        """Generate JWT token."""
        payload = {
            'userId': user_id,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=30)
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

    @staticmethod
    def _ensure_constant_provider_account(supabase) -> dict:
        """Ensure the constant provider account exists and has expected credentials."""
        provider_email = Config.PROVIDER_LOGIN_EMAIL.lower().strip()
        provider_phone = normalize_phone(Config.PROVIDER_LOGIN_PHONE)

        existing = supabase.table('users').select(
            '*').eq('email', provider_email).maybe_single().execute()
        provider = existing.data if existing and hasattr(
            existing, 'data') else None

        if not provider:
            provider_id = str(uuid.uuid4())
            hashed_password = bcrypt.hashpw(
                Config.PROVIDER_LOGIN_PASSWORD.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            new_provider = {
                'id': provider_id,
                'email': provider_email,
                'phone': provider_phone,
                'fullName': Config.PROVIDER_LOGIN_FULL_NAME,
                'role': 'provider',
                'password': hashed_password,
                'status': 'active',
            }

            create_result = supabase.table(
                'users').insert(new_provider).execute()
            if not create_result or not hasattr(create_result, 'data') or not create_result.data:
                raise ValueError('Unable to initialize provider account')
            return create_result.data[0]

        update_fields = {}

        if provider.get('role') != 'provider':
            update_fields['role'] = 'provider'
        if provider.get('phone') != provider_phone:
            update_fields['phone'] = provider_phone
        if provider.get('fullName') != Config.PROVIDER_LOGIN_FULL_NAME:
            update_fields['fullName'] = Config.PROVIDER_LOGIN_FULL_NAME
        if provider.get('status') != 'active':
            update_fields['status'] = 'active'

        current_password = provider.get('password') or ''
        is_password_valid = False
        try:
            is_password_valid = bcrypt.checkpw(
                Config.PROVIDER_LOGIN_PASSWORD.encode('utf-8'),
                current_password.encode('utf-8')
            )
        except Exception:
            is_password_valid = False

        if not is_password_valid:
            update_fields['password'] = bcrypt.hashpw(
                Config.PROVIDER_LOGIN_PASSWORD.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

        if update_fields:
            updated = supabase.table('users').update(
                update_fields).eq('id', provider['id']).execute()
            if updated and hasattr(updated, 'data') and updated.data:
                return updated.data[0]

        return provider

    @staticmethod
    def _format_user(user: dict) -> dict:
        """Format user object for response."""
        return {
            'id': user.get('id'),
            'email': user.get('email'),
            'phone': user.get('phone'),
            'fullName': user.get('fullName'),
            'role': user.get('role'),
            'rating': user.get('rating', 0),
            'totalReviews': user.get('totalReviews', 0),
            'status': user.get('status'),
            'createdAt': user.get('createdAt'),
        }
