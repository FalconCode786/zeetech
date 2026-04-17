"""Main application entry point."""
import os
from app import create_app
from app.utils.supabase_client import init_supabase

if __name__ == '__main__':
    # Initialize Supabase
    init_supabase()

    # Create Flask app
    app = create_app()

    # Run development server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    print(f'\n✓ ZeeTech Flask Backend starting on http://localhost:{port}')
    print(f'✓ Environment: {os.getenv("FLASK_ENV", "development")}')
    print(f'✓ Debug mode: {debug}\n')

    app.run(host='127.0.0.1', port=port, debug=debug)
