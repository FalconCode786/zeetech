"""Helper utility functions"""

from datetime import datetime, timezone
from flask import jsonify
from bson.objectid import ObjectId


def object_id(obj):
    """Convert string to ObjectId if valid, otherwise raise error"""
    try:
        return ObjectId(obj)
    except Exception:
        return None


def is_valid_object_id(obj_id):
    """Check if string is a valid MongoDB ObjectId"""
    if isinstance(obj_id, ObjectId):
        return True
    try:
        ObjectId(obj_id)
        return True
    except Exception:
        return False


def get_timestamp():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_response(data=None, message=None, code=200):
    """Format a standard JSON response"""
    response = {}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), code


def serialize_document(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None

    if isinstance(doc, list):
        return [serialize_document(item) for item in doc]

    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_document(value)
            elif isinstance(value, list):
                result[key] = serialize_document(value)
            else:
                result[key] = value
        return result

    if isinstance(doc, ObjectId):
        return str(doc)

    if isinstance(doc, datetime):
        return doc.isoformat()

    return doc


def pagination_params(request):
    """Extract pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Validate pagination params
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100

    skip = (page - 1) * limit

    return {
        'page': page,
        'limit': limit,
        'skip': skip
    }


def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Simple phone validation (international format)"""
    import re
    # Matches phone numbers like +1234567890 or 1234567890
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None
