#!/usr/bin/env python
"""
Test database connection script.

This script tests the database connection using the provided credentials.
"""
import os
import sys
import logging
import psycopg2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_db_connection():
    """Test the database connection using the provided credentials."""
    # Database credentials
    db_name = "buyzaar"
    db_user = "dmtavs"
    db_password = "Dmt@1212"
    db_host = "localhost"
    db_port = "5432"
    
    # Try to connect to the database
    try:
        logger.info(f"Connecting to database {db_name} on {db_host}:{db_port} as {db_user}")
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        
        # Execute a simple query
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            logger.info(f"Connected to database: {version}")
        
        # Create a test table
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS test_connection (id SERIAL PRIMARY KEY, name TEXT);")
            conn.commit()
            logger.info("Created test table")
            
            # Insert a test record
            cur.execute("INSERT INTO test_connection (name) VALUES (%s) RETURNING id;", ("Test connection",))
            record_id = cur.fetchone()[0]
            conn.commit()
            logger.info(f"Inserted test record with ID {record_id}")
            
            # Query the test record
            cur.execute("SELECT name FROM test_connection WHERE id = %s;", (record_id,))
            name = cur.fetchone()[0]
            logger.info(f"Retrieved test record: {name}")
            
            # Delete the test record
            cur.execute("DELETE FROM test_connection WHERE id = %s;", (record_id,))
            conn.commit()
            logger.info("Deleted test record")
        
        conn.close()
        logger.info("Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

if __name__ == '__main__':
    try:
        if test_db_connection():
            logger.info("Database connection test passed")
            sys.exit(0)
        else:
            logger.error("Database connection test failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Database connection test failed with error: {str(e)}")
        sys.exit(1)