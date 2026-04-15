"""Feedback routes for booking feedback and ratings"""

from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models.feedback import Feedback
from app.models.booking import Booking
from app.utils.errors import ValidationError, NotFoundError
from app.utils.helpers import serialize_document

feedbacks_bp = Blueprint('feedbacks', __name__, url_prefix='/api/feedbacks')


@feedbacks_bp.route('/', methods=['POST'])
@login_required
def create_feedback():
    """Create feedback for a booking (required before payment)"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        booking_id = data.get('bookingId')
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not booking_id:
            return {'error': 'Booking ID is required', 'code': 'MISSING_FIELD'}, 400

        if rating is None or not isinstance(rating, int) or not (1 <= rating <= 5):
            return {'error': 'Rating must be an integer between 1 and 5', 'code': 'INVALID_RATING'}, 400

        # Verify booking belongs to current user
        booking = Booking.find_by_id(booking_id)
        if not booking:
            return {'error': 'Booking not found', 'code': 'NOT_FOUND'}, 404

        if str(booking.customer_id) != str(current_user.id):
            return {'error': 'Unauthorized', 'code': 'FORBIDDEN'}, 403

        # Check if feedback already exists
        existing_feedback = Feedback.find_by_booking(booking_id)
        if existing_feedback:
            return {'error': 'Feedback already provided for this booking', 'code': 'DUPLICATE'}, 409

        # Create feedback
        feedback = Feedback(
            booking_id=booking_id,
            customer_id=str(current_user.id),
            rating=rating,
            comment=comment
        )

        if feedback.save():
            # Update booking with feedback ID
            booking.feedback_id = feedback.id
            booking.save()

            return {
                'message': 'Feedback created successfully',
                'data': feedback.to_dict()
            }, 201

        return {'error': 'Failed to save feedback', 'code': 'SAVE_ERROR'}, 500

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@feedbacks_bp.route('/by-booking/<booking_id>', methods=['GET'])
@login_required
def get_feedback(booking_id):
    """Get feedback for a specific booking"""
    try:
        feedback = Feedback.find_by_booking(booking_id)

        if not feedback:
            return {'error': 'Feedback not found', 'code': 'NOT_FOUND'}, 404

        # Verify authorization
        booking = Booking.find_by_id(booking_id)
        if not booking:
            return {'error': 'Booking not found', 'code': 'NOT_FOUND'}, 404

        if str(booking.customer_id) != str(current_user.id) and str(booking.provider_id) != str(current_user.id):
            return {'error': 'Unauthorized', 'code': 'FORBIDDEN'}, 403

        return {
            'message': 'Feedback retrieved successfully',
            'data': feedback.to_dict()
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@feedbacks_bp.route('/<int:feedback_id>', methods=['PUT'])
@login_required
def update_feedback(feedback_id):
    """Update existing feedback"""
    try:
        data = request.get_json()

        if not data:
            return {'error': 'Request body is required', 'code': 'INVALID_REQUEST'}, 400

        feedback = Feedback.find_by_id(feedback_id)
        if not feedback:
            return {'error': 'Feedback not found', 'code': 'NOT_FOUND'}, 404

        # Verify authorization
        if str(feedback.customer_id) != str(current_user.id):
            return {'error': 'Unauthorized', 'code': 'FORBIDDEN'}, 403

        # Update fields
        if 'rating' in data:
            rating = data.get('rating')
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                return {'error': 'Rating must be an integer between 1 and 5', 'code': 'INVALID_RATING'}, 400
            feedback.rating = rating

        if 'comment' in data:
            comment = data.get('comment', '')
            if len(comment) > 1000:
                return {'error': 'Comment must be less than 1000 characters', 'code': 'INVALID_COMMENT'}, 400
            feedback.comment = comment

        if feedback.save():
            return {
                'message': 'Feedback updated successfully',
                'data': feedback.to_dict()
            }, 200

        return {'error': 'Failed to update feedback', 'code': 'SAVE_ERROR'}, 500

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@feedbacks_bp.route('/<int:feedback_id>', methods=['DELETE'])
@login_required
def delete_feedback(feedback_id):
    """Delete feedback"""
    try:
        feedback = Feedback.find_by_id(feedback_id)
        if not feedback:
            return {'error': 'Feedback not found', 'code': 'NOT_FOUND'}, 404

        # Verify authorization
        if str(feedback.customer_id) != str(current_user.id):
            return {'error': 'Unauthorized', 'code': 'FORBIDDEN'}, 403

        # Delete from database
        from app.models.database import get_feedbacks_collection
        feedbacks_collection = get_feedbacks_collection()

        try:
            feedbacks_collection.delete().eq('id', feedback_id).execute()
            return {'message': 'Feedback deleted successfully'}, 200
        except Exception as e:
            return {'error': f'Delete failed: {str(e)}', 'code': 'DELETE_ERROR'}, 500

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500


@feedbacks_bp.route('/customer/<customer_id>', methods=['GET'])
def get_customer_feedbacks(customer_id):
    """Get all feedbacks from a customer"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 10, type=int)

        feedbacks = Feedback.find_by_customer(customer_id, skip, limit)

        return {
            'message': 'Feedbacks retrieved successfully',
            'data': [f.to_dict() for f in feedbacks]
        }, 200

    except Exception as e:
        return {'error': str(e), 'code': 'INTERNAL_ERROR'}, 500
