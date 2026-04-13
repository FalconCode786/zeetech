"""Provider service management"""

from bson.objectid import ObjectId
from app.models.database import get_users_collection, get_bookings_collection, get_provider_services_collection
from app.utils.helpers import get_timestamp, is_valid_object_id, pagination_params
from app.models.user import User
from datetime import datetime


class ProviderService:
    """Service for managing provider operations"""

    @staticmethod
    def get_provider_services(provider_id, skip=0, limit=10):
        """Get all services offered by a provider"""
        if not is_valid_object_id(provider_id):
            raise ValueError('Invalid provider ID')

        collection = get_provider_services_collection()
        provider_services = list(collection.find(
            {'provider_id': ObjectId(provider_id)},
            {'_id': 1, 'subcategory_name': 1,
                'price': 1, 'status': 1, 'created_at': 1}
        ).skip(skip).limit(limit))

        total = collection.count_documents(
            {'provider_id': ObjectId(provider_id)})

        return provider_services, total

    @staticmethod
    def create_provider_service(provider_id, data):
        """Create a new service offering by provider"""
        if not is_valid_object_id(provider_id):
            raise ValueError('Invalid provider ID')

        subcategory_name = data.get('subcategoryName')
        price = data.get('price')
        description = data.get('description')

        if not subcategory_name or not price:
            raise ValueError('subcategoryName and price are required')

        collection = get_provider_services_collection()

        service_data = {
            'provider_id': ObjectId(provider_id),
            'subcategory_name': subcategory_name,
            'price': float(price),
            'description': description,
            'status': 'active',
            'created_at': get_timestamp(),
            'updated_at': get_timestamp()
        }

        result = collection.insert_one(service_data)

        return {
            '_id': str(result.inserted_id),
            'provider_id': provider_id,
            'subcategory_name': subcategory_name,
            'price': price,
            'description': description,
            'status': 'active',
            'createdAt': service_data['created_at'].isoformat() if isinstance(service_data['created_at'], datetime) else service_data['created_at']
        }

    @staticmethod
    def update_provider_service(provider_id, service_id, data):
        """Update a provider's service"""
        if not is_valid_object_id(provider_id) or not is_valid_object_id(service_id):
            raise ValueError('Invalid provider or service ID')

        collection = get_provider_services_collection()

        # Verify service belongs to provider
        existing = collection.find_one({
            '_id': ObjectId(service_id),
            'provider_id': ObjectId(provider_id)
        })

        if not existing:
            raise ValueError(
                'Service not found or does not belong to this provider')

        update_data = {
            'updated_at': get_timestamp()
        }

        if 'price' in data:
            update_data['price'] = float(data['price'])
        if 'subcategoryName' in data:
            update_data['subcategory_name'] = data['subcategoryName']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'status' in data:
            update_data['status'] = data['status']

        result = collection.update_one(
            {'_id': ObjectId(service_id)},
            {'$set': update_data}
        )

        if result.modified_count == 0:
            raise ValueError('Failed to update service')

        updated = collection.find_one({'_id': ObjectId(service_id)})

        return {
            '_id': str(updated['_id']),
            'provider_id': provider_id,
            'subcategory_name': updated.get('subcategory_name'),
            'price': updated.get('price'),
            'description': updated.get('description'),
            'status': updated.get('status'),
            'updatedAt': updated['updated_at'].isoformat() if isinstance(updated['updated_at'], datetime) else updated['updated_at']
        }

    @staticmethod
    def delete_provider_service(provider_id, service_id):
        """Delete a provider's service"""
        if not is_valid_object_id(provider_id) or not is_valid_object_id(service_id):
            raise ValueError('Invalid provider or service ID')

        collection = get_provider_services_collection()

        # Verify service belongs to provider
        existing = collection.find_one({
            '_id': ObjectId(service_id),
            'provider_id': ObjectId(provider_id)
        })

        if not existing:
            raise ValueError(
                'Service not found or does not belong to this provider')

        result = collection.delete_one({'_id': ObjectId(service_id)})

        if result.deleted_count == 0:
            raise ValueError('Failed to delete service')

        return True

    @staticmethod
    def get_provider_bookings(provider_id, status=None, skip=0, limit=10):
        """Get all bookings for a provider"""
        if not is_valid_object_id(provider_id):
            raise ValueError('Invalid provider ID')

        collection = get_bookings_collection()
        query = {'provider_id': ObjectId(provider_id)}

        if status:
            query['status'] = status

        bookings = list(collection.find(query).skip(
            skip).limit(limit).sort('created_at', -1))
        total = collection.count_documents(query)

        return bookings, total

    @staticmethod
    def get_booking_detail(provider_id, booking_id):
        """Get booking details (provider can only see their own)"""
        if not is_valid_object_id(provider_id) or not is_valid_object_id(booking_id):
            raise ValueError('Invalid provider or booking ID')

        collection = get_bookings_collection()
        booking = collection.find_one({
            '_id': ObjectId(booking_id),
            'provider_id': ObjectId(provider_id)
        })

        if not booking:
            raise ValueError(
                'Booking not found or does not belong to this provider')

        return booking

    @staticmethod
    def confirm_booking(provider_id, booking_id):
        """Confirm/accept a booking"""
        if not is_valid_object_id(provider_id) or not is_valid_object_id(booking_id):
            raise ValueError('Invalid provider or booking ID')

        collection = get_bookings_collection()

        booking = collection.find_one({
            '_id': ObjectId(booking_id),
            'provider_id': ObjectId(provider_id),
            'status': 'assigned'
        })

        if not booking:
            raise ValueError(
                'Booking not found, does not belong to this provider, or is not in assigned status')

        result = collection.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': {
                'status': 'confirmed',
                'confirmed_at': get_timestamp(),
                'updated_at': get_timestamp()
            }}
        )

        if result.modified_count == 0:
            raise ValueError('Failed to confirm booking')

        return True

    @staticmethod
    def start_booking(provider_id, booking_id):
        """Start work on a booking (mark as in_progress)"""
        if not is_valid_object_id(provider_id) or not is_valid_object_id(booking_id):
            raise ValueError('Invalid provider or booking ID')

        collection = get_bookings_collection()

        booking = collection.find_one({
            '_id': ObjectId(booking_id),
            'provider_id': ObjectId(provider_id),
            'status': 'confirmed'
        })

        if not booking:
            raise ValueError(
                'Booking not found, does not belong to this provider, or is not in confirmed status')

        result = collection.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': {
                'status': 'in_progress',
                'updated_at': get_timestamp()
            }}
        )

        if result.modified_count == 0:
            raise ValueError('Failed to start booking')

        return True

    @staticmethod
    def complete_booking(provider_id, booking_id, data=None):
        """Complete a booking"""
        if not is_valid_object_id(provider_id) or not is_valid_object_id(booking_id):
            raise ValueError('Invalid provider or booking ID')

        collection = get_bookings_collection()

        booking = collection.find_one({
            '_id': ObjectId(booking_id),
            'provider_id': ObjectId(provider_id),
            'status': 'in_progress'
        })

        if not booking:
            raise ValueError(
                'Booking not found, does not belong to this provider, or is not in progress')

        update_obj = {
            'status': 'completed',
            'completed_at': get_timestamp(),
            'updated_at': get_timestamp()
        }

        if data and 'additionalCharges' in data:
            update_obj['additional_charges'] = float(data['additionalCharges'])

        result = collection.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': update_obj}
        )

        if result.modified_count == 0:
            raise ValueError('Failed to complete booking')

        return True

    @staticmethod
    def cancel_booking(provider_id, booking_id, reason=None):
        """Cancel a booking"""
        if not is_valid_object_id(provider_id) or not is_valid_object_id(booking_id):
            raise ValueError('Invalid provider or booking ID')

        collection = get_bookings_collection()

        booking = collection.find_one({
            '_id': ObjectId(booking_id),
            'provider_id': ObjectId(provider_id)
        })

        if not booking:
            raise ValueError(
                'Booking not found or does not belong to this provider')

        # Can't cancel if already completed or cancelled
        if booking['status'] in ['completed', 'cancelled']:
            raise ValueError(
                f'Cannot cancel booking with status: {booking["status"]}')

        update_obj = {
            'status': 'cancelled',
            'updated_at': get_timestamp()
        }

        if reason:
            update_obj['cancellation_reason'] = reason

        result = collection.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': update_obj}
        )

        if result.modified_count == 0:
            raise ValueError('Failed to cancel booking')

        return True

    @staticmethod
    def get_provider_stats(provider_id):
        """Get provider statistics"""
        if not is_valid_object_id(provider_id):
            raise ValueError('Invalid provider ID')

        bookings_collection = get_bookings_collection()

        total_bookings = bookings_collection.count_documents(
            {'provider_id': ObjectId(provider_id)})
        completed_bookings = bookings_collection.count_documents(
            {'provider_id': ObjectId(provider_id), 'status': 'completed'}
        )
        pending_bookings = bookings_collection.count_documents(
            {'provider_id': ObjectId(provider_id), 'status': 'assigned'}
        )
        in_progress = bookings_collection.count_documents(
            {'provider_id': ObjectId(provider_id), 'status': 'in_progress'}
        )

        return {
            'totalBookings': total_bookings,
            'completedBookings': completed_bookings,
            'pendingBookings': pending_bookings,
            'inProgress': in_progress
        }
