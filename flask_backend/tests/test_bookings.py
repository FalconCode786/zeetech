"""Unit tests for bookings"""

import pytest
from app import create_app
from app.models.database import initialize_database, drop_database
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)

    with app.app_context():
        initialize_database()

        # Create service categories for testing
        from app.models.database import get_categories_collection
        categories_collection = get_categories_collection()

        # Insert test service categories
        categories_collection.insert_one({
            'name': 'AC Maintenance',
            'displayOrder': 1,
            'subcategories': [
                {
                    'name': 'AC Repair',
                    'basePrice': 100,
                    'description': 'AC repair service'
                },
                {
                    'name': 'AC Installation',
                    'basePrice': 150,
                    'description': 'AC installation service'
                }
            ]
        })

        yield app
        drop_database()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def customer(client):
    """Create and login a customer"""
    client.post('/api/auth/register', json={
        'email': 'customer@example.com',
        'phone': '+1111111111',
        'fullName': 'Customer User',
        'password': 'password123',
        'role': 'customer'
    })

    client.post('/api/auth/login', json={
        'email': 'customer@example.com',
        'password': 'password123'
    })

    return client


@pytest.fixture
def provider(client):
    """Create and login a provider"""
    client.post('/api/auth/register', json={
        'email': 'provider@example.com',
        'phone': '+2222222222',
        'fullName': 'Provider User',
        'password': 'password123',
        'role': 'provider'
    })

    client.post('/api/auth/login', json={
        'email': 'provider@example.com',
        'password': 'password123'
    })

    return client


class TestBookings:
    """Booking management tests"""

    def test_create_booking(self, customer):
        """Test creating a booking"""
        response = customer.post('/api/bookings', json={
            'subcategoryName': 'AC Repair',
            'baseAmount': 100,
            'preferredDate': '2026-04-20',
            'preferredTimeSlot': '10:00-11:00',
            'location': {
                'address': '123 Main St',
                'city': 'New York',
                'area': 'Downtown'
            },
            'problemDescription': 'AC not cooling'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['booking']['status'] == 'pending'
        assert data['data']['booking']['baseAmount'] == 100

    def test_list_bookings(self, customer):
        """Test listing customer bookings"""
        # Create a booking first
        customer.post('/api/bookings', json={
            'subcategoryName': 'AC Repair',
            'baseAmount': 100,
            'preferredDate': '2026-04-20'
        })

        response = customer.get('/api/bookings')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['bookings']) > 0

    def test_filter_bookings_by_status(self, customer):
        """Test filtering bookings by status"""
        # Create a booking
        customer.post('/api/bookings', json={
            'subcategoryName': 'AC Repair',
            'baseAmount': 100,
            'preferredDate': '2026-04-20'
        })

        response = customer.get('/api/bookings?status=pending')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['bookings']) == 1
        assert data['data']['bookings'][0]['status'] == 'pending'

    def test_get_booking_detail(self, customer):
        """Test getting booking details"""
        # Create a booking
        create_response = customer.post('/api/bookings', json={
            'subcategoryName': 'AC Repair',
            'baseAmount': 100,
            'preferredDate': '2026-04-20'
        })

        booking_id = create_response.get_json()['data']['booking']['_id']

        response = customer.get(f'/api/bookings/{booking_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['booking']['_id'] == booking_id

    def test_update_booking_status(self, customer):
        """Test updating booking status"""
        # Create a booking
        create_response = customer.post('/api/bookings', json={
            'subcategoryName': 'AC Repair',
            'baseAmount': 100,
            'preferredDate': '2026-04-20'
        })

        booking_id = create_response.get_json()['data']['booking']['_id']

        # Update status
        response = customer.put(f'/api/bookings/{booking_id}/status', json={
            'status': 'confirmed'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['booking']['status'] == 'confirmed'

    def test_invalid_status_transition(self, customer):
        """Test invalid booking status transition"""
        # Create a booking
        create_response = customer.post('/api/bookings', json={
            'subcategoryName': 'AC Repair',
            'baseAmount': 100,
            'preferredDate': '2026-04-20'
        })

        booking_id = create_response.get_json()['data']['booking']['_id']

        # Try invalid transition (pending -> in_progress)
        response = customer.put(f'/api/bookings/{booking_id}/status', json={
            'status': 'in_progress'
        })

        assert response.status_code == 422


class TestBookingCalculations:
    """Test booking amount calculations"""

    def test_total_amount_calculation(self, customer):
        """Test total amount with charges and discounts"""
        response = customer.post('/api/bookings', json={
            'subcategoryName': 'AC Repair',
            'baseAmount': 100,
            'preferredDate': '2026-04-20',
            'additionalCharges': 20,
            'discountAmount': 10
        })

        data = response.get_json()
        # 100 + 20 - 10 = 110
        assert data['data']['booking']['totalAmount'] == 110
