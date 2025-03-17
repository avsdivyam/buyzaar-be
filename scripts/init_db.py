#!/usr/bin/env python
"""
Database initialization script.

This script initializes the database with required tables and initial data.
"""
import os
import sys
import logging

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from app import db, create_app
from app.models import User
from app.utils.db_utils import check_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with tables and initial data."""
    # Create the Flask app with the specified configuration
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        # Check database connection
        if not check_db_connection(db):
            logger.error("Failed to connect to the database. Please check your database configuration.")
            sys.exit(1)
        
        logger.info("Creating database tables...")
        db.create_all()
        
        # Check if admin user exists
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@buyzaar.com')
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Should be changed in production
        
        admin = User.get_by_email(admin_email)
        if not admin:
            logger.info(f"Creating admin user: {admin_username}")
            admin = User(
                email=admin_email,
                username=admin_username,
                password_hash='temporary_hash',  # In a real app, you would hash the password
                first_name='Admin',
                last_name='User',
                is_active=True,
                is_admin=True
            )
            admin.save()
            logger.info("Admin user created successfully")
        else:
            logger.info("Admin user already exists")
        
        logger.info("Database initialization completed successfully")

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)