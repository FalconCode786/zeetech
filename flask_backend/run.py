#!/usr/bin/env python
"""Entry point for running the Flask application"""

import os
from app import create_app

# Create Flask app
app = create_app()

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', True)

    print(f"Starting ZeeTech Flask Backend on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
