"""Supabase client initialization and utilities."""
import os
from supabase import create_client, Client

_supabase_client: Client = None

def get_supabase() -> Client:
    """Get or create Supabase client."""
    global _supabase_client
    
    if _supabase_client is None:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError('SUPABASE_URL and SUPABASE_KEY must be set')
        
        _supabase_client = create_client(url, key)
        print('✓ Supabase client initialized')
    
    return _supabase_client

def init_supabase():
    """Initialize Supabase connection."""
    try:
        client = get_supabase()
        print('✓ Supabase initialized successfully')
        return client
    except Exception as e:
        print(f'✗ Failed to initialize Supabase: {str(e)}')
        return None
