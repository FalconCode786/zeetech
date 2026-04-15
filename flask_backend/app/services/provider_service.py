"""Provider service management"""

from app.models.database import get_users_collection, get_bookings_collection, get_provider_services_collection
from app.utils.helpers import get_timestamp, is_valid_object_id, pagination_params
from app.models.user import User
from datetime import datetime


class ProviderService:
    """Service for managing provider operations"""

    @staticmethod
    def get_provider_services(provider_id, skip=0, limit=10):
        """Get all services offered by a provider"""
        from app.models.database import supabase_client

        try:
            # Get total count
            count_response = supabase_client.table('providerServices').select(
                'id', count='exact').eq('providerId', str(provider_id)).execute()
            total = count_response.count if count_response.count else 0

            # Get paginated results
            start = skip
            end = skip + limit - 1
            response = supabase_client.table('providerServices').select('id, subcategoryName, price, status, createdAt').eq(
                'providerId', str(provider_id)).range(start, end).execute()

            provider_services = response.data if response.data else []
            return provider_services, total
        except Exception as e:
            print(f"Error fetching provider services: {e}")
            return [], 0

    @staticmethod
    def create_provider_service(provider_id, data):
        """Create a new service offering by provider"""
        from app.models.database import supabase_client

        subcategory_name = data.get('subcategoryName')
        price = data.get('price')
        description = data.get('description')

        if not subcategory_name or not price:
            raise ValueError('subcategoryName and price are required')

        try:
            service_data = {
                'providerId': str(provider_id),
                'subcategoryName': subcategory_name,
                'price': float(price),
                'description': description,
                'status': 'active',
                'createdAt': get_timestamp()
            }

            response = supabase_client.table(
                'providerServices').insert(service_data).execute()

            if response.data and len(response.data) > 0:
                result = response.data[0]
                return {
                    'id': result.get('id'),
                    'providerId': provider_id,
                    'subcategoryName': subcategory_name,
                    'price': price,
                    'description': description,
                    'status': 'active',
                    'createdAt': result.get('createdAt')
                }
            raise Exception('Failed to create service')
        except Exception as e:
            print(f"Error creating provider service: {e}")
            raise

    @staticmethod
    def update_provider_service(provider_id, service_id, data):
        """Update a provider's service"""
        from app.models.database import supabase_client

        try:
            # Verify service belongs to provider
            verify = supabase_client.table('providerServices').select('id').eq(
                'id', int(service_id)).eq('providerId', str(provider_id)).execute()

            if not verify.data:
                raise ValueError(
                    'Service not found or does not belong to this provider')

            update_data = {}

            if 'price' in data:
                update_data['price'] = float(data['price'])
            if 'subcategoryName' in data:
                update_data['subcategoryName'] = data['subcategoryName']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'status' in data:
                update_data['status'] = data['status']

            response = supabase_client.table('providerServices').update(
                update_data).eq('id', int(service_id)).execute()

            if response.data:
                result = response.data[0]
                return {
                    'id': result.get('id'),
                    'providerId': provider_id,
                    'subcategoryName': result.get('subcategoryName'),
                    'price': result.get('price'),
                    'description': result.get('description'),
                    'status': result.get('status'),
                    'updatedAt': result.get('updatedAt')
                }
            raise ValueError('Failed to update service')
        except Exception as e:
            print(f"Error updating provider service: {e}")
            raise

    @staticmethod
    def delete_provider_service(provider_id, service_id):
        """Delete a provider's service"""
        from app.models.database import supabase_client

        try:
            # Verify service belongs to provider
            verify = supabase_client.table('providerServices').select('id').eq(
                'id', int(service_id)).eq('providerId', str(provider_id)).execute()

            if not verify.data:
                raise ValueError(
                    'Service not found or does not belong to this provider')

            response = supabase_client.table('providerServices').delete().eq(
                'id', int(service_id)).execute()
            return True
        except Exception as e:
            print(f"Error deleting provider service: {e}")
            raise

    @staticmethod
    def get_provider_bookings(provider_id, status=None, skip=0, limit=10):
        """Get all bookings for a provider"""
        from app.models.database import supabase_client

        try:
            # Build query
            query = supabase_client.table('bookings').select(
                '*').eq('providerId', str(provider_id))

            if status:
                query = query.eq('status', status)

            # Get total count
            count_query = supabase_client.table('bookings').select(
                'id', count='exact').eq('providerId', str(provider_id))
            if status:
                count_query = count_query.eq('status', status)
            count_response = count_query.execute()
            total = count_response.count if count_response.count else 0

            # Get paginated results
            start = skip
            end = skip + limit - 1
            response = query.order('createdAt', desc=True).range(
                start, end).execute()

            bookings = response.data if response.data else []
            return bookings, total
        except Exception as e:
            print(f"Error fetching provider bookings: {e}")
            return [], 0

    @staticmethod
    def get_booking_detail(provider_id, booking_id):
        """Get booking details (provider can only see their own)"""
        from app.models.database import supabase_client

        try:
            response = supabase_client.table('bookings').select(
                '*').eq('id', int(booking_id)).eq('providerId', str(provider_id)).execute()

            if not response.data:
                raise ValueError(
                    'Booking not found or does not belong to this provider')

            return response.data[0]
        except Exception as e:
            print(f"Error fetching booking detail: {e}")
            raise

    @staticmethod
    def confirm_booking(provider_id, booking_id):
        """Confirm/accept a booking"""
        from app.models.database import supabase_client

        try:
            # Verify booking belongs to provider and is in correct status
            verify = supabase_client.table('bookings').select('id').eq('id', int(booking_id)).eq(
                'providerId', str(provider_id)).eq('status', 'assigned').execute()

            if not verify.data:
                raise ValueError(
                    'Booking not found, does not belong to this provider, or is not in assigned status')

            response = supabase_client.table('bookings').update(
                {'status': 'confirmed', 'confirmedAt': get_timestamp()}).eq('id', int(booking_id)).execute()

            return response.data is not None
        except Exception as e:
            print(f"Error confirming booking: {e}")
            raise

    @staticmethod
    def start_booking(provider_id, booking_id):
        """Start work on a booking (mark as in_progress)"""
        from app.models.database import supabase_client

        try:
            # Verify booking belongs to provider and is in correct status
            verify = supabase_client.table('bookings').select('id').eq('id', int(booking_id)).eq(
                'providerId', str(provider_id)).eq('status', 'confirmed').execute()

            if not verify.data:
                raise ValueError(
                    'Booking not found, does not belong to this provider, or is not in confirmed status')

            response = supabase_client.table('bookings').update(
                {'status': 'in_progress'}).eq('id', int(booking_id)).execute()

            return response.data is not None
        except Exception as e:
            print(f"Error starting booking: {e}")
            raise

    @staticmethod
    def complete_booking(provider_id, booking_id, data=None):
        """Complete a booking"""
        from app.models.database import supabase_client

        try:
            # Verify booking belongs to provider and is in progress
            verify = supabase_client.table('bookings').select('id').eq('id', int(booking_id)).eq(
                'providerId', str(provider_id)).eq('status', 'in_progress').execute()

            if not verify.data:
                raise ValueError(
                    'Booking not found, does not belong to this provider, or is not in progress')

            update_obj = {'status': 'completed',
                          'completedAt': get_timestamp()}

            if data and 'additionalCharges' in data:
                update_obj['additionalCharges'] = float(
                    data['additionalCharges'])

            response = supabase_client.table('bookings').update(
                update_obj).eq('id', int(booking_id)).execute()

            return response.data is not None
        except Exception as e:
            print(f"Error completing booking: {e}")
            raise

    @staticmethod
    def cancel_booking(provider_id, booking_id, reason=None):
        """Cancel a booking"""
        from app.models.database import supabase_client

        try:
            # Get booking to check status
            booking_response = supabase_client.table('bookings').select('status').eq(
                'id', int(booking_id)).eq('providerId', str(provider_id)).execute()

            if not booking_response.data:
                raise ValueError(
                    'Booking not found or does not belong to this provider')

            booking = booking_response.data[0]

            # Can't cancel if already completed or cancelled
            if booking['status'] in ['completed', 'cancelled']:
                raise ValueError(
                    f"Cannot cancel booking with status: {booking['status']}")

            update_obj = {'status': 'cancelled'}
            if reason:
                update_obj['cancellationReason'] = reason

            response = supabase_client.table('bookings').update(
                update_obj).eq('id', int(booking_id)).execute()

            return response.data is not None
        except Exception as e:
            print(f"Error cancelling booking: {e}")
            raise

    @staticmethod
    def get_provider_stats(provider_id):
        """Get provider statistics"""
        from app.models.database import supabase_client

        try:
            # Get total bookings
            total_response = supabase_client.table('bookings').select(
                'id', count='exact').eq('providerId', str(provider_id)).execute()
            total_bookings = total_response.count if total_response.count else 0

            # Get completed bookings
            completed_response = supabase_client.table('bookings').select('id', count='exact').eq(
                'providerId', str(provider_id)).eq('status', 'completed').execute()
            completed_bookings = completed_response.count if completed_response.count else 0

            # Get pending bookings
            pending_response = supabase_client.table('bookings').select('id', count='exact').eq(
                'providerId', str(provider_id)).eq('status', 'assigned').execute()
            pending_bookings = pending_response.count if pending_response.count else 0

            # Get in_progress bookings
            in_progress_response = supabase_client.table('bookings').select('id', count='exact').eq(
                'providerId', str(provider_id)).eq('status', 'in_progress').execute()
            in_progress = in_progress_response.count if in_progress_response.count else 0

            return {
                'totalBookings': total_bookings,
                'completedBookings': completed_bookings,
                'pendingBookings': pending_bookings,
                'inProgress': in_progress
            }
        except Exception as e:
            print(f"Error getting provider stats: {e}")
            return {
                'totalBookings': 0,
                'completedBookings': 0,
                'pendingBookings': 0,
                'inProgress': 0
            }
