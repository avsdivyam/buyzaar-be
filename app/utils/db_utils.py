"""
Database utility functions.

This module provides utility functions for database operations.
"""
import time
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError
from functools import wraps

logger = logging.getLogger(__name__)

def with_db_retry(max_retries=3, retry_delay=1):
    """
    Decorator to retry database operations on connection errors.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        Function decorator
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError) as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Database operation failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    logger.warning(f"Database connection error, retrying ({retries}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay * retries)  # Exponential backoff
                except SQLAlchemyError as e:
                    logger.error(f"Database error: {str(e)}")
                    raise
        return wrapper
    return decorator

def check_db_connection(db):
    """
    Check if the database connection is alive.
    
    Args:
        db: SQLAlchemy database instance
        
    Returns:
        bool: True if connection is alive, False otherwise
    """
    try:
        # Execute a simple query to check connection
        db.session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

def initialize_db(app, db):
    """
    Initialize the database with proper error handling.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    try:
        with app.app_context():
            # Check if we can connect to the database
            if check_db_connection(db):
                app.logger.info("Database connection successful")
            else:
                app.logger.error("Failed to connect to the database")
                
            # Create all tables if they don't exist
            db.create_all()
            app.logger.info("Database tables created or verified")
    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        # Don't raise the exception to allow the app to start even with DB issues
        # This allows the app to retry connections later