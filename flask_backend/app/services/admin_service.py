"""Admin operations business logic"""

from app.models.booking import Booking
from app.models.user import User
from app.utils.errors import ValidationError, NotFoundError


class AdminService:
    """Service for admin operations"""

    @staticmethod
    def get_all_bookings(status=None, skip=0, limit=10):
        """
        Get all bookings in the system

        Args:
            status: Filter by status (optional)
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            tuple: (bookings list, total count)
        """
        bookings = Booking.find_all(status=status, skip=skip, limit=limit)
        total = Booking.count_all(status=status)

        return bookings, total

    @staticmethod
    def get_all_users(role=None, skip=0, limit=10):
        """
        Get all users in the system

        Args:
            role: Filter by role (customer/provider)
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            tuple: (users list, total count)
        """
        from app.models.database import supabase_client

        try:
            query = supabase_client.table('users').select('*')

            if role:
                query = query.eq('role', role)

            # Get total count
            total_response = supabase_client.table(
                'users').select('id', count='exact')
            if role:
                total_response = total_response.eq('role', role)
            total_response = total_response.execute()
            total = total_response.count if total_response.count else 0

            # Get paginated results
            start = skip
            end = skip + limit - 1
            response = query.range(start, end).execute()

            users = []
            if response.data:
                for doc in response.data:
                    users.append(User._from_doc(doc))

            return users, total
        except Exception as e:
            print(f"Error fetching users: {e}")
            return [], 0

    @staticmethod
    def get_system_stats():
        """
        Get system statistics

        Returns:
            dict: System stats
        """
        from app.models.database import supabase_client

        try:
            # Count users by role
            total_users_response = supabase_client.table(
                'users').select('id', count='exact').execute()
            total_users = total_users_response.count if total_users_response.count else 0

            active_users_response = supabase_client.table('users').select(
                'id', count='exact').eq('status', 'active').execute()
            active_users = active_users_response.count if active_users_response.count else 0

            customers_response = supabase_client.table('users').select(
                'id', count='exact').eq('role', 'customer').execute()
            customers = customers_response.count if customers_response.count else 0

            providers_response = supabase_client.table('users').select(
                'id', count='exact').eq('role', 'provider').execute()
            providers = providers_response.count if providers_response.count else 0

            # Count bookings by status
            total_bookings_response = supabase_client.table(
                'bookings').select('id', count='exact').execute()
            total_bookings = total_bookings_response.count if total_bookings_response.count else 0

            pending_bookings_response = supabase_client.table('bookings').select(
                'id', count='exact').eq('status', 'pending').execute()
            pending_bookings = pending_bookings_response.count if pending_bookings_response.count else 0

            completed_bookings_response = supabase_client.table('bookings').select(
                'id', count='exact').eq('status', 'completed').execute()
            completed_bookings = completed_bookings_response.count if completed_bookings_response.count else 0

            # Count categories
            categories_response = supabase_client.table(
                'serviceCategories').select('id', count='exact').execute()
            total_categories = categories_response.count if categories_response.count else 0

            # Calculate total revenue from completed bookings
            completed_bookings_data = supabase_client.table('bookings').select(
                'totalAmount').eq('status', 'completed').execute()
            total_revenue = 0
            if completed_bookings_data.data:
                total_revenue = sum([b.get('totalAmount', 0)
                                    for b in completed_bookings_data.data])

            return {
                'totalUsers': total_users,
                'activeUsers': active_users,
                'customers': customers,
                'providers': providers,
                'totalBookings': total_bookings,
                'pendingBookings': pending_bookings,
                'completedBookings': completed_bookings,
                'totalCategories': total_categories,
                'totalRevenue': total_revenue
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {
                'totalUsers': 0,
                'activeUsers': 0,
                'customers': 0,
                'providers': 0,
                'totalBookings': 0,
                'pendingBookings': 0,
                'completedBookings': 0,
                'totalCategories': 0,
                'totalRevenue': 0
            }

    @staticmethod
    def deactivate_user(user_id):
        """
        Deactivate a user account

        Args:
            user_id: User ID to deactivate

        Returns:
            User: Updated user
        """
        user = User.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found')

        user.status = 'inactive'
        if user.save():
            return user

        raise Exception('Failed to deactivate user')

    @staticmethod
    def activate_user(user_id):
        """
        Activate a user account

        Args:
            user_id: User ID to activate

        Returns:
            User: Updated user
        """
        user = User.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found')

        user.status = 'active'
        if user.save():
            return user

        raise Exception('Failed to activate user')

    @staticmethod
    def get_booking_breakdown():
        """
        Get booking statistics by status

        Returns:
            dict: Breakdown by status
        """
        from app.models.database import supabase_client

        try:
            statuses = ['pending', 'assigned',
                        'in_progress', 'completed', 'cancelled']
            breakdown = {}

            for status in statuses:
                count_response = supabase_client.table('bookings').select(
                    'id', count='exact').eq('status', status).execute()
                count = count_response.count if count_response.count else 0

                bookings_response = supabase_client.table('bookings').select(
                    'totalAmount').eq('status', status).execute()
                total_amount = 0
                if bookings_response.data:
                    total_amount = sum([b.get('totalAmount', 0)
                                       for b in bookings_response.data])

                breakdown[status] = {
                    'count': count,
                    'totalAmount': total_amount
                }

            return breakdown
        except Exception as e:
            print(f"Error getting booking breakdown: {e}")
            return {}

    @staticmethod
    def get_provider_performance():
        """
        Get top performing providers by booking count and rating

        Returns:
            list: Top providers
        """
        from app.models.database import supabase_client
        from app.models.rating import Rating

        try:
            # Get all completed bookings
            response = supabase_client.table('bookings').select(
                'providerId, totalAmount').eq('status', 'completed').execute()

            if not response.data:
                return []

            # Group by provider
            provider_stats = {}
            for booking in response.data:
                provider_id = booking.get('providerId')
                if not provider_id:
                    continue

                if provider_id not in provider_stats:
                    provider_stats[provider_id] = {
                        'completedJobs': 0,
                        'totalRevenue': 0
                    }

                provider_stats[provider_id]['completedJobs'] += 1
                provider_stats[provider_id]['totalRevenue'] += booking.get(
                    'totalAmount', 0)

            # Sort by completed jobs and get top 10
            sorted_providers = sorted(
                provider_stats.items(),
                key=lambda x: x[1]['completedJobs'],
                reverse=True
            )[:10]

            # Build result with ratings
            result = []
            for provider_id, stats in sorted_providers:
                avg_rating, _count = Rating.get_provider_average_rating(
                    provider_id)
                result.append({
                    'providerId': str(provider_id),
                    'completedJobs': stats['completedJobs'],
                    'totalRevenue': stats['totalRevenue'],
                    'averageRating': avg_rating
                })

            return result
        except Exception as e:
            print(f"Error getting provider performance: {e}")
            return []
