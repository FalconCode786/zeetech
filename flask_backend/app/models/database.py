"""MongoDB database initialization and collection management"""

from app import get_db
from bson.objectid import ObjectId
from datetime import datetime


def initialize_database():
    """Initialize MongoDB database with collections and indexes"""
    db = get_db()

    # Create collections
    collections = [
        'users',
        'service_categories',
        'bookings',
        'ratings',
        'provider_services'
    ]

    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"Created collection: {collection_name}")

    # Create indexes
    # Users collection indexes
    db['users'].create_index('email', unique=True)
    db['users'].create_index('phone', unique=True)
    db['users'].create_index('role')
    db['users'].create_index('createdAt')

    # Service categories indexes
    db['service_categories'].create_index('name')
    db['service_categories'].create_index('displayOrder')

    # Bookings collection indexes
    db['bookings'].create_index('customerId')
    db['bookings'].create_index('providerId')
    db['bookings'].create_index('status')
    db['bookings'].create_index('createdAt')
    db['bookings'].create_index([('customerId', 1), ('status', 1)])

    # Ratings collection indexes
    db['ratings'].create_index('bookingId', unique=True)
    db['ratings'].create_index('providerId')
    db['ratings'].create_index('customerId')

    # Provider services indexes
    db['provider_services'].create_index('providerId')
    db['provider_services'].create_index('status')
    db['provider_services'].create_index([('providerId', 1), ('status', 1)])

    print("Database indexes created successfully")


def drop_database():
    """Drop the entire database (use with caution - for testing only)"""
    db = get_db()
    db.client.drop_database(db.name)
    print(f"Database {db.name} dropped")


# Collection helpers
def get_users_collection():
    """Get users collection"""
    return get_db()['users']


def get_categories_collection():
    """Get service_categories collection"""
    return get_db()['service_categories']


def get_bookings_collection():
    """Get bookings collection"""
    return get_db()['bookings']


def get_ratings_collection():
    """Get ratings collection"""
    return get_db()['ratings']


def get_provider_services_collection():
    """Get provider_services collection"""
    return get_db()['provider_services']
