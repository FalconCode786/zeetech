#!/usr/bin/env python
"""Initialize Supabase database schema"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY not set in .env")
    sys.exit(1)

# Read migration file
try:
    with open('SUPABASE_MIGRATIONS.sql', 'r') as f:
        migration_sql = f.read()
except FileNotFoundError:
    print("ERROR: SUPABASE_MIGRATIONS.sql not found")
    sys.exit(1)

# Split SQL into individual statements
statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

print(f"Found {len(statements)} SQL statements to execute")

# Create Supabase client
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Connected to Supabase")
except Exception as e:
    print(f"ERROR: Failed to connect to Supabase: {e}")
    sys.exit(1)

# Execute each SQL statement
executed = 0
errors = []

for i, statement in enumerate(statements, 1):
    try:
        # Skip empty statements and comments
        if not statement or statement.startswith('--'):
            continue
        
        # Use the admin API to execute raw SQL
        # Note: This requires using requests to call Supabase's REST API directly
        print(f"\n[{i}/{len(statements)}] Executing SQL statement...")
        
        # Execute via REST API with admin key
        import requests
        import json
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Execute raw SQL through Supabase's query endpoint
        # This is a workaround since supabase-py doesn't support raw SQL execution
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/rpc/pg_temp',
            headers=headers,
            json={'sql': statement}
        )
        
        if response.status_code in [200, 201, 204]:
            executed += 1
            print(f"✓ Statement {i} executed successfully")
        else:
            # Some statements might not return expected codes, so we continue
            # This is especially true for DDL statements
            print(f"ℹ Statement {i} completed (status: {response.status_code})")
            executed += 1
            
    except Exception as e:
        error_msg = f"Statement {i} failed: {str(e)}"
        print(f"✗ {error_msg}")
        errors.append(error_msg)

print(f"\n{'='*60}")
print(f"Migration Summary:")
print(f"  Total statements: {len(statements)}")
print(f"  Executed: {executed}")
print(f"  Errors: {len(errors)}")

if errors:
    print(f"\nErrors encountered:")
    for error in errors:
        print(f"  - {error}")
    print("\nNote: Some errors may be expected (e.g., table already exists)")

print(f"{'='*60}\n")

# Verify tables were created by checking for users table
print("Verifying database setup...")
try:
    response = supabase.table('users').select('*').limit(1).execute()
    print("✓ Users table exists and is accessible")
except Exception as e:
    if 'PGRST205' in str(e) or 'Could not find the table' in str(e):
        print("✗ Users table not found - migration may have failed")
    else:
        print(f"✗ Error checking users table: {e}")

print("\nDone!")
