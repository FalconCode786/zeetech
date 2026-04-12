"""Unit tests for authentication"""

import pytest
import json
from app import create_app, get_db
from app.models.database import initialize_database, drop_database
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)

    with app.app_context():
        # Initialize test database
        initialize_database()
        yield app
        # Cleanup
        drop_database()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


class TestAuth:
    """Authentication tests"""

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'phone': '+1234567890',
            'fullName': 'Test User',
            'password': 'password123',
            'role': 'customer'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert data['data']['user']['email'] == 'test@example.com'

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/api/auth/register', json={
            'email': 'invalid-email',
            'phone': '+1234567890',
            'fullName': 'Test User',
            'password': 'password123'
        })

        assert response.status_code == 422
        data = response.get_json()
        assert 'VALIDATION_ERROR' in data['code']

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # First registration
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'phone': '+1234567890',
            'fullName': 'Test User',
            'password': 'password123'
        })

        # Second registration with same email
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'phone': '+9876543210',
            'fullName': 'Another User',
            'password': 'password123'
        })

        assert response.status_code == 409
        data = response.get_json()
        assert 'CONFLICT' in data['code']

    def test_login_success(self, client):
        """Test successful login"""
        # Register first
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'phone': '+1234567890',
            'fullName': 'Test User',
            'password': 'password123'
        })

        # Login
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'UNAUTHORIZED' in data['code']

    def test_verify_auth_required(self, client):
        """Test verify endpoint requires authentication"""
        response = client.get('/api/auth/verify')

        assert response.status_code == 401

    def test_verify_authenticated(self, client):
        """Test verify endpoint with authenticated user"""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'phone': '+1234567890',
            'fullName': 'Test User',
            'password': 'password123'
        })

        client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Verify
        response = client.get('/api/auth/verify')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['user']['email'] == 'test@example.com'


class TestUsers:
    """User profile tests"""

    def test_update_profile(self, client):
        """Test updating user profile"""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'phone': '+1234567890',
            'fullName': 'Test User',
            'password': 'password123'
        })

        client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Get user ID from verify
        verify_response = client.get('/api/auth/verify')
        user_id = verify_response.get_json()['data']['user']['_id']

        # Update profile
        response = client.put(f'/api/users/{user_id}', json={
            'city': 'New York',
            'address': '123 Main St'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['user']['city'] == 'New York'
