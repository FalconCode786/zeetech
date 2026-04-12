"""Admin operations business logic"""

from app.models.booking import Booking
from app.models.user import User
from app.utils.errors import ValidationError, NotFoundError
from bson.objectid import ObjectId


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
        from app.models.database import get_users_collection

        users_collection = get_users_collection()
        query = {}

        if role:
            query['role'] = role

        cursor = users_collection.find(query).skip(skip).limit(limit)

        users = []
        for doc in cursor:
            users.append(User._from_doc(doc))

        total = users_collection.count_documents(query)

        return users, total

    @staticmethod
    def get_system_stats():
        """
        Get system statistics

        Returns:
            dict: System stats
        """
        from app.models.database import get_bookings_collection, get_users_collection, get_categories_collection

        bookings_collection = get_bookings_collection()
        users_collection = get_users_collection()
        categories_collection = get_categories_collection()

        # Count documents
        total_bookings = bookings_collection.count_documents({})
        total_users = users_collection.count_documents({})
        active_users = users_collection.count_documents({'status': 'active'})
        customers = users_collection.count_documents({'role': 'customer'})
        providers = users_collection.count_documents({'role': 'provider'})
        total_categories = categories_collection.count_documents({})

        # Booking stats
        pending_bookings = bookings_collection.count_documents(
            {'status': 'pending'})
        completed_bookings = bookings_collection.count_documents(
            {'status': 'completed'})

        # Revenue stats
        revenue_pipeline = [
            {'$match': {'status': 'completed'}},
            {'$group': {
                '_id': None,
                'totalRevenue': {'$sum': '$totalAmount'}
            }}
        ]

        revenue_result = list(bookings_collection.aggregate(revenue_pipeline))
        total_revenue = revenue_result[0]['totalRevenue'] if revenue_result else 0

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
        from app.models.database import get_bookings_collection

        bookings_collection = get_bookings_collection()

        pipeline = [
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1},
                    'totalAmount': {'$sum': '$totalAmount'}
                }
            }
        ]

        results = list(bookings_collection.aggregate(pipeline))

        breakdown = {}
        for result in results:
            breakdown[result['_id']] = {
                'count': result['count'],
                'totalAmount': result['totalAmount']
            }

        return breakdown

    @staticmethod
    def get_provider_performance():
        """
        Get top performing providers by booking count and rating

        Returns:
            list: Top providers
        """
        from app.models.database import get_bookings_collection, get_users_collection
        from app.models.rating import Rating

        bookings_collection = get_bookings_collection()
        users_collection = get_users_collection()

        # Get providers with completed bookings
        pipeline = [
            {'$match': {'status': 'completed', 'providerId': {'$ne': None}}},
            {
                '$group': {
                    '_id': '$providerId',
                    'completedJobs': {'$sum': 1},
                    'totalRevenue': {'$sum': '$totalAmount'}
                }
            },
            {'$sort': {'completedJobs': -1}},
            {'$limit': 10}
        ]

        providers_performance = list(bookings_collection.aggregate(pipeline))

        # Add rating info
        result = []
        for provider_data in providers_performance:
            provider_id = provider_data['_id']
            result.append({
                'providerId': str(provider_id),
                'completedJobs': provider_data['completedJobs'],
                'totalRevenue': provider_data['totalRevenue'],
                'averageRating': Rating.get_provider_average_rating(provider_id)[0]
            })

        return result
