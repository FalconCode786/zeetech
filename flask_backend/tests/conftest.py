"""Pytest configuration and fixtures"""

import os
import sys

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def pytest_configure(config):
    """Configure pytest"""
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'
