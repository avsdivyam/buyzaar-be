#!/usr/bin/env python
"""
Database connection check script.

This script checks if the database connection is working properly.
"""
import os
import sys
import logging
import psycopg2

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_db_connection():
    """Check if the database connection is working properly."""
    # Get database connection parameters from environment variables
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        db_url = os.environ.get('DEV_DATABASE_URL')
    
    if not db_url:
        logger.error("No database URL found in environment variables")
        return False
    
    # Parse database URL
    if db_url.startswith('postgresql://'):
        # Extract connection parameters from URL
        db_url = db_url.replace('postgresql://', '')
        user_pass, host_db = db_url.split('@')
        
        if ':' in user_pass:
            user, password = user_pass.split(':')
        else:
            user = user_pass
            password = ''
        
        if '/' in host_db:
            host_port, db = host_db.split('/')
        else:
            host_port = host_db
            db = ''
        
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 5432
    else:
        logger.error(f"Unsupported database URL format: {db_url}")
        return False
    
    # Try to connect to the database
    try:
        logger.info(f"Connecting to database {db} on {host}:{port} as {user}")
        conn = psycopg2.connect(
            dbname=db,
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        # Execute a simple query
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            logger.info(f"Connected to database: {version}")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return False

if __name__ == '__main__':
    try:
        if check_db_connection():
            logger.info("Database connection check passed")
            sys.exit(0)
        else:
            logger.error("Database connection check failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Database connection check failed with error: {str(e)}")
        sys.exit(1)