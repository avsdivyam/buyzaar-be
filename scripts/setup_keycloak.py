#!/usr/bin/env python
"""
Keycloak setup script.

This script sets up the Keycloak realm and client for the application.
"""
import os
import sys
import logging
import requests
import json
import base64

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_keycloak():
    """Set up the Keycloak realm and client for the application."""
    # Get Keycloak connection parameters from environment variables
    keycloak_url = os.environ.get('KEYCLOAK_SERVER_URL', 'http://3.6.134.85:8080/')
    keycloak_realm = os.environ.get('KEYCLOAK_REALM', 'buyzaar')
    keycloak_client_id = os.environ.get('KEYCLOAK_CLIENT_ID', 'buyzaar-client')
    keycloak_admin = os.environ.get('KEYCLOAK_ADMIN', 'admin')
    keycloak_admin_password = os.environ.get('KEYCLOAK_ADMIN_PASSWORD', 'admin')
    
    # Remove trailing slash if present
    if keycloak_url.endswith('/'):
        keycloak_url = keycloak_url[:-1]
    
    # Get admin token
    try:
        logger.info(f"Getting admin token from Keycloak at {keycloak_url}")
        response = requests.post(
            f"{keycloak_url}/realms/master/protocol/openid-connect/token",
            data={
                'grant_type': 'password',
                'client_id': 'admin-cli',
                'username': keycloak_admin,
                'password': keycloak_admin_password
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get admin token: {response.text}")
            return False
        
        admin_token = response.json()['access_token']
        logger.info("Got admin token")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get admin token: {str(e)}")
        return False
    
    # Check if realm exists
    try:
        logger.info(f"Checking if realm {keycloak_realm} exists")
        response = requests.get(
            f"{keycloak_url}/admin/realms/{keycloak_realm}",
            headers={
                'Authorization': f'Bearer {admin_token}'
            },
            timeout=10
        )
        
        realm_exists = response.status_code == 200
        
        if realm_exists:
            logger.info(f"Realm {keycloak_realm} already exists")
        else:
            logger.info(f"Realm {keycloak_realm} does not exist, creating it")
            
            # Create realm
            response = requests.post(
                f"{keycloak_url}/admin/realms",
                json={
                    'realm': keycloak_realm,
                    'enabled': True,
                    'displayName': 'BuyZaar',
                    'displayNameHtml': '<div class="kc-logo-text"><span>BuyZaar</span></div>',
                    'loginTheme': 'keycloak',
                    'accountTheme': 'keycloak',
                    'adminTheme': 'keycloak',
                    'emailTheme': 'keycloak',
                    'accessTokenLifespan': 900,  # 15 minutes
                    'ssoSessionIdleTimeout': 1800,  # 30 minutes
                    'ssoSessionMaxLifespan': 36000,  # 10 hours
                    'offlineSessionIdleTimeout': 2592000,  # 30 days
                    'accessCodeLifespan': 60,  # 1 minute
                    'accessCodeLifespanUserAction': 300,  # 5 minutes
                    'accessCodeLifespanLogin': 1800,  # 30 minutes
                    'bruteForceProtected': True,
                    'permanentLockout': False,
                    'maxFailureWaitSeconds': 900,  # 15 minutes
                    'minimumQuickLoginWaitSeconds': 60,  # 1 minute
                    'waitIncrementSeconds': 60,  # 1 minute
                    'quickLoginCheckMilliSeconds': 1000,  # 1 second
                    'maxDeltaTimeSeconds': 43200,  # 12 hours
                    'failureFactor': 3  # 3 failures
                },
                headers={
                    'Authorization': f'Bearer {admin_token}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create realm: {response.text}")
                return False
            
            logger.info(f"Created realm {keycloak_realm}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to check if realm exists: {str(e)}")
        return False
    
    # Check if client exists
    try:
        logger.info(f"Checking if client {keycloak_client_id} exists")
        response = requests.get(
            f"{keycloak_url}/admin/realms/{keycloak_realm}/clients",
            params={
                'clientId': keycloak_client_id
            },
            headers={
                'Authorization': f'Bearer {admin_token}'
            },
            timeout=10
        )
        
        clients = response.json()
        client_exists = len(clients) > 0
        
        if client_exists:
            logger.info(f"Client {keycloak_client_id} already exists")
            client_id = clients[0]['id']
        else:
            logger.info(f"Client {keycloak_client_id} does not exist, creating it")
            
            # Create client
            response = requests.post(
                f"{keycloak_url}/admin/realms/{keycloak_realm}/clients",
                json={
                    'clientId': keycloak_client_id,
                    'enabled': True,
                    'name': 'BuyZaar Client',
                    'description': 'BuyZaar Client',
                    'rootUrl': 'http://localhost:5173',
                    'adminUrl': 'http://localhost:5173',
                    'baseUrl': 'http://localhost:5173',
                    'redirectUris': [
                        'http://localhost:5173/*',
                        'http://localhost:5000/*'
                    ],
                    'webOrigins': [
                        'http://localhost:5173',
                        'http://localhost:5000'
                    ],
                    'publicClient': False,
                    'directAccessGrantsEnabled': True,
                    'standardFlowEnabled': True,
                    'implicitFlowEnabled': False,
                    'serviceAccountsEnabled': True,
                    'authorizationServicesEnabled': True,
                    'fullScopeAllowed': True
                },
                headers={
                    'Authorization': f'Bearer {admin_token}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create client: {response.text}")
                return False
            
            # Get client ID
            response = requests.get(
                f"{keycloak_url}/admin/realms/{keycloak_realm}/clients",
                params={
                    'clientId': keycloak_client_id
                },
                headers={
                    'Authorization': f'Bearer {admin_token}'
                },
                timeout=10
            )
            
            clients = response.json()
            client_id = clients[0]['id']
            
            logger.info(f"Created client {keycloak_client_id} with ID {client_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to check if client exists: {str(e)}")
        return False
    
    # Get client secret
    try:
        logger.info(f"Getting client secret for client {keycloak_client_id}")
        response = requests.get(
            f"{keycloak_url}/admin/realms/{keycloak_realm}/clients/{client_id}/client-secret",
            headers={
                'Authorization': f'Bearer {admin_token}'
            },
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get client secret: {response.text}")
            return False
        
        client_secret = response.json()['value']
        logger.info(f"Client secret: {client_secret}")
        
        # Update .env file with client secret
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            if 'KEYCLOAK_CLIENT_SECRET=' in env_content:
                env_content = env_content.replace(
                    'KEYCLOAK_CLIENT_SECRET=your-client-secret',
                    f'KEYCLOAK_CLIENT_SECRET={client_secret}'
                )
                
                with open(env_file, 'w') as f:
                    f.write(env_content)
                
                logger.info(f"Updated .env file with client secret")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get client secret: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    try:
        if setup_keycloak():
            logger.info("Keycloak setup completed successfully")
            sys.exit(0)
        else:
            logger.error("Keycloak setup failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Keycloak setup failed with error: {str(e)}")
        sys.exit(1)