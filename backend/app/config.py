import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    # Flask
    DEBUG = False
    TESTING = False

    # Database (Supabase)
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

    # JWT
    JWT_SECRET = os.getenv(
        'JWT_SECRET', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24 * 30  # 30 days

    # Constant provider login credentials used for demo/testing.
    PROVIDER_LOGIN_EMAIL = 'provider@zeetech.com'
    PROVIDER_LOGIN_PHONE = '03001234567'
    PROVIDER_LOGIN_PASSWORD = 'Provider@123!'
    PROVIDER_LOGIN_FULL_NAME = 'ZeeTech Provider'

    # API
    API_TIMEOUT = 30
    API_BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8080')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True


# Get the active config
config_name = os.getenv('FLASK_ENV', 'development')
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
