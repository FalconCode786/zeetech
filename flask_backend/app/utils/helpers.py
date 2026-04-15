"""Helper utility functions"""

from datetime import datetime, timezone
from flask import jsonify
import uuid


def object_id(obj):
    """Placeholder for legacy ObjectId logic, now returns string ID or None"""
    if not obj:
        return None
    return str(obj)


def is_valid_object_id(obj_id):
    """Check if string is a valid UUID or ID (depends on Supabase schema)"""
    if not obj_id:
        return False
    try:
        uuid.UUID(str(obj_id))
        return True
    except ValueError:
        return isinstance(obj_id, int) or isinstance(obj_id, str)


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
    """Convert Supabase dictionary to JSON-serializable dict"""
    if doc is None:
        return None

    if isinstance(doc, list):
        return [serialize_document(item) for item in doc]

    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_document(value)
            elif isinstance(value, list):
                result[key] = serialize_document(value)
            else:
                result[key] = value
        return result

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
    """Validate phone number (Pakistan format: +92 or 03xx)"""
    import re
    # Accept various formats: +92XXXXXXXXXX, 03XXXXXXXXX, 92XXXXXXXXXX
    pattern = r'^(\+92|92|0)[3-9]\d{8,9}$'
    return re.match(pattern, str(phone).replace(' ', '').replace('-', '')) is not None
