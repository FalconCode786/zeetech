#!/usr/bin/env python
"""
Initialize Supabase database by creating tables programmatically

Instructions:
1. Copy the SQL from SUPABASE_MIGRATIONS.sql
2. Open your Supabase dashboard at: https://app.supabase.com/
3. Navigate to SQL Editor (left sidebar)
4. Click "New Query"
5. Paste the SQL from SUPABASE_MIGRATIONS.sql
6. Click "Run" button

Alternatively, you can run this script if you have supabase CLI installed:
    supabase db push
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("""
╔════════════════════════════════════════════════════════════════╗
║        ZeeTech Backend - Supabase Database Setup              ║
╚════════════════════════════════════════════════════════════════╝

To initialize your Supabase database, follow these steps:

1. Open Supabase Dashboard
   URL: https://app.supabase.com/

2. Log in to your project

3. Click "SQL Editor" in the left sidebar

4. Click "New Query" button

5. Copy and paste the following SQL file content:
   File: SUPABASE_MIGRATIONS.sql

6. Click the "Run" button

7. Wait for all statements to execute

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your Supabase Details:
  Project URL: {SUPABASE_URL}
  
To verify the setup after running the SQL:
  1. Click "Table Editor" in left sidebar
  2. You should see these tables:
     - users
     - serviceCategories
     - providerServices
     - bookings
     - ratings
     - feedbacks
     - payments

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quick Setup Using Supabase CLI (if installed):

  1. Install supabase CLI:
     npm install -g supabase

  2. Navigate to backend directory:
     cd flask_backend

  3. Create migrations directory:
     mkdir -p supabase/migrations

  4. Copy this file:
     cp SUPABASE_MIGRATIONS.sql supabase/migrations/001_init_schema.sql

  5. Link to your project:
     supabase link --project-ref <your-project-id>

  6. Push migrations:
     supabase db push

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING:

If you get an error about "users" table already existing:
  → That's fine! The migrations use CREATE TABLE IF NOT EXISTS
  → The schema is already set up

If tables don't appear after running SQL:
  → Refresh the page browser
  → Check the SQL Editor output for errors
  → Ensure you're in the correct project

If you get permission errors:
  → Use your service role key instead of anon key
  → Or run SQL directly in Supabase dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Once database is initialized, test the backend:

  1. In a terminal, run:
     python run.py

  2. In another terminal, test registration:
     curl -X POST http://localhost:5000/api/auth/register \\
       -H "Content-Type: application/json" \\
       -d '{
         "email": "test@example.com",
         "phone": "03001234567",
         "fullName": "Test User",
         "password": "password123",
         "role": "customer"
       }'

  3. Expected response (201 Created):
     {{
       "message": "User registered successfully",
       "token": "...",
       "user": {{...}}
     }}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".format(SUPABASE_URL=SUPABASE_URL))

print("\nTo proceed with the setup, please:")
print("1. Copy all content from SUPABASE_MIGRATIONS.sql")
print("2. Go to https://app.supabase.com/")
print("3. Open SQL Editor and create new query")
print("4. Paste the SQL and run it")
print("\n" + "="*70)
