"""Rating and review routes"""

from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.rating_service import RatingService
from app.utils.errors import AppError
from app.utils.helpers import serialize_document, is_valid_object_id, pagination_params

ratings_bp = Blueprint('ratings', __name__, url_prefix='/api/ratings')


@ratings_bp.route('/bookings/<booking_id>', methods=['POST'])
@login_required
def create_rating(booking_id):
    """Create a rating for a completed booking"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        # Only customers can create ratings
        if current_user.role != 'customer':
            return {'error': 'Only customers can rate bookings', 'code': 'FORBIDDEN'}, 403

        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        rating_value = data.get('rating')
        review = data.get('review')

        rating = RatingService.create_rating(
            booking_id,
            current_user.get_id(),
            rating_value,
            review
        )

        return {
            'message': 'Rating created successfully',
            'data': {
                'rating': serialize_document(rating.to_dict())
            }
        }, 201

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@ratings_bp.route('/bookings/<booking_id>', methods=['GET'])
def get_booking_rating(booking_id):
    """Get rating for a booking"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        rating = RatingService.get_booking_rating(booking_id)

        if not rating:
            return {
                'message': 'No rating found for this booking',
                'data': {'rating': None}
            }, 200

        return {
            'message': 'Rating retrieved successfully',
            'data': {
                'rating': serialize_document(rating.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@ratings_bp.route('/bookings/<booking_id>', methods=['PUT'])
@login_required
def update_rating(booking_id):
    """Update a rating"""
    try:
        if not is_valid_object_id(booking_id):
            return {'error': 'Invalid booking ID', 'code': 'INVALID_ID'}, 400

        # Get the rating
        rating = RatingService.get_booking_rating(booking_id)
        if not rating:
            return {'error': 'Rating not found', 'code': 'NOT_FOUND'}, 404

        # Only the customer who created the rating can update it
        if str(rating.customer_id) != current_user.get_id():
            return {'error': 'Can only update your own ratings', 'code': 'FORBIDDEN'}, 403

        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        rating = RatingService.update_rating(rating._id, data)

        return {
            'message': 'Rating updated successfully',
            'data': {
                'rating': serialize_document(rating.to_dict())
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@ratings_bp.route('/providers/<provider_id>', methods=['GET'])
def get_provider_ratings(provider_id):
    """Get all ratings for a provider"""
    try:
        if not is_valid_object_id(provider_id):
            return {'error': 'Invalid provider ID', 'code': 'INVALID_ID'}, 400

        # Get pagination params
        params = pagination_params(request)

        ratings, total, avg_rating = RatingService.get_provider_ratings(
            provider_id,
            skip=params['skip'],
            limit=params['limit']
        )

        # Serialize ratings
        ratings_data = [serialize_document(r.to_dict()) for r in ratings]

        return {
            'message': 'Provider ratings retrieved successfully',
            'data': {
                'ratings': ratings_data,
                'providerStats': {
                    'providerId': provider_id,
                    'averageRating': round(avg_rating, 2),
                    'totalRatings': total
                },
                'pagination': {
                    'page': params['page'],
                    'limit': params['limit'],
                    'total': total
                }
            }
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@ratings_bp.route('/providers/<provider_id>/stats', methods=['GET'])
def get_provider_stats(provider_id):
    """Get rating statistics for a provider"""
    try:
        if not is_valid_object_id(provider_id):
            return {'error': 'Invalid provider ID', 'code': 'INVALID_ID'}, 400

        stats = RatingService.get_provider_stats(provider_id)

        return {
            'message': 'Provider statistics retrieved successfully',
            'data': stats
        }, 200

    except AppError as e:
        return {'error': e.message, 'code': e.code}, e.status_code
    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
