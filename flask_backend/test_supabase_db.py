#!/usr/bin/env python
"""
Test Supabase database connection and schema
Run this after applying SUPABASE_MIGRATIONS.sql
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL and SUPABASE_KEY not set in .env")
    sys.exit(1)

print("🔍 Testing Supabase Connection...\n")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

# Test tables
tables = [
    'users',
    'serviceCategories',
    'providerServices',
    'bookings',
    'ratings',
    'feedbacks',
    'payments'
]

print("\n📋 Checking tables...\n")
missing_tables = []

for table in tables:
    try:
        response = supabase.table(table).select('id', count='exact').limit(1).execute()
        print(f"  ✅ {table}: OK (count: {response.count})")
    except Exception as e:
        if 'Could not find the table' in str(e) or 'PGRST205' in str(e):
            print(f"  ❌ {table}: NOT FOUND")
            missing_tables.append(table)
        else:
            print(f"  ⚠️  {table}: Error - {str(e)[:50]}")

if missing_tables:
    print(f"\n❌ Missing tables: {', '.join(missing_tables)}")
    print("\n📝 Database Setup Instructions:")
    print("   1. Go to https://app.supabase.com/")
    print("   2. Open SQL Editor")
    print("   3. Create new query and paste SUPABASE_MIGRATIONS.sql")
    print("   4. Run the SQL")
    print("   5. Run this script again to verify")
    sys.exit(1)
else:
    print("\n✅ All required tables exist!")
    print("\n✨ Database initialization complete!")
    print("\nYou can now start the backend:")
    print("   python run.py")
