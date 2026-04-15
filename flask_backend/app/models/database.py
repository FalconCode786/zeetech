"""Supabase database collection references"""


def get_db():
    from app import supabase_client
    if supabase_client is None:
        raise Exception("Supabase client is not initialized")
    return supabase_client


def get_users_collection():
    return get_db().table('users')


def get_categories_collection():
    return get_db().table('service_categories')


def get_bookings_collection():
    return get_db().table('bookings')


def get_ratings_collection():
    return get_db().table('ratings')


def get_feedbacks_collection():
    return get_db().table('feedbacks')


def get_provider_services_collection():
    return get_db().table('provider_services')


def get_payments_collection():
    return get_db().table('payments')


def initialize_database():
    print("Supabase structure requires migrations via SQL. No init needed here.")


def drop_database():
    print("Not applicable to Supabase.")
