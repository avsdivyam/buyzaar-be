#!/usr/bin/env python
"""
Keycloak connection check script.

This script checks if the Keycloak connection is working properly.
"""
import os
import sys
import logging
import requests

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_keycloak_connection():
    """Check if the Keycloak connection is working properly."""
    # Get Keycloak connection parameters from environment variables
    keycloak_url = os.environ.get('KEYCLOAK_SERVER_URL', 'http://3.6.134.85:8080/')
    keycloak_realm = os.environ.get('KEYCLOAK_REALM', 'buyzaar')
    
    # Remove trailing slash if present
    if keycloak_url.endswith('/'):
        keycloak_url = keycloak_url[:-1]
    
    # Check if Keycloak is running
    try:
        logger.info(f"Checking Keycloak connection at {keycloak_url}")
        response = requests.get(f"{keycloak_url}/health", timeout=5)
        
        if response.status_code == 200:
            logger.info("Keycloak health check passed")
            return True
        else:
            logger.error(f"Keycloak health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to Keycloak: {str(e)}")
        
        # Try alternative endpoint
        try:
            logger.info("Trying alternative Keycloak endpoint")
            response = requests.get(f"{keycloak_url}/realms/{keycloak_realm}/.well-known/openid-configuration", timeout=5)
            
            if response.status_code == 200:
                logger.info("Keycloak realm configuration check passed")
                return True
            else:
                logger.error(f"Keycloak realm configuration check failed with status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Keycloak realm: {str(e)}")
            return False

if __name__ == '__main__':
    try:
        if check_keycloak_connection():
            logger.info("Keycloak connection check passed")
            sys.exit(0)
        else:
            logger.error("Keycloak connection check failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Keycloak connection check failed with error: {str(e)}")
        sys.exit(1)