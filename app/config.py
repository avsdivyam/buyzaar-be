"""
Application configuration module.

This module defines configuration classes for different environments.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # API configuration
    API_TITLE = 'E-Commerce API'
    API_VERSION = 'v1'
    
    # Pagination configuration
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # Keycloak configuration
    KEYCLOAK_SERVER_URL = os.environ.get('KEYCLOAK_SERVER_URL')
    KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM')
    KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID')
    KEYCLOAK_CLIENT_SECRET = os.environ.get('KEYCLOAK_CLIENT_SECRET')
    
    # Google Drive configuration
    GOOGLE_CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""
        # Configure logging
        import logging
        from app.core.logging import configure_logging
        configure_logging(app, Config.LOG_LEVEL)


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True

    # Use the DEV_DATABASE_URL from environment variables
    # If not set, fall back to a default SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///dev-app.db'

    # Database connection settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Detect and reconnect to database if connection is lost
        'pool_recycle': 300,    # Recycle connections after 5 minutes
        'pool_size': 10,        # Maximum number of connections to keep in the pool
        'max_overflow': 20      # Maximum number of connections to create above pool_size
    }

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Log to console
        import logging
        app.logger.setLevel(logging.DEBUG)

        # Log database connection info (but not credentials)
        db_url = os.environ.get('DEV_DATABASE_URL', '')
        if db_url:
            # Extract just the database type and name for logging (not credentials)
            parts = db_url.split('@')
            if len(parts) > 1:
                db_info = parts[1]
            else:
                db_info = parts[0].split('://')[0] if '://' in parts[0] else parts[0]
            app.logger.info(f"Using database: {db_info}")


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'
    
    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    # Use the DATABASE_URL from environment variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Database connection settings for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,      # Detect and reconnect to database if connection is lost
        'pool_recycle': 300,        # Recycle connections after 5 minutes
        'pool_size': 20,            # Maximum number of connections to keep in the pool
        'max_overflow': 40,         # Maximum number of connections to create above pool_size
        'pool_timeout': 30,         # Timeout for getting a connection from the pool
        'connect_args': {
            'connect_timeout': 10   # Connection timeout in seconds
        }
    }

    # Additional security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

        # Validate that DATABASE_URL is set
        if not os.environ.get('DATABASE_URL'):
            app.logger.error("DATABASE_URL environment variable is not set. Application may not function correctly.")

        # Log database connection info (but not credentials)
        db_url = os.environ.get('DATABASE_URL', '')
        if db_url:
            # Extract just the database type and name for logging (not credentials)
            parts = db_url.split('@')
            if len(parts) > 1:
                db_info = parts[1]
            else:
                db_info = parts[0].split('://')[0] if '://' in parts[0] else parts[0]
            app.logger.info(f"Using database: {db_info}")


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}