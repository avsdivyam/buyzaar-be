from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.services.keycloak import KeycloakService

def get_token_from_header():
    """
    Extract token from Authorization header
    
    Returns:
        str: Token or None
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    return auth_header.split(' ')[1]

def validate_token(token):
    """
    Validate a JWT token with Keycloak
    
    Args:
        token (str): JWT token
    
    Returns:
        dict: Token info or None if invalid
    """
    try:
        keycloak_service = KeycloakService()
        return keycloak_service.keycloak_openid.introspect(token)
    except Exception as e:
        current_app.logger.error(f"Token validation error: {str(e)}")
        return None

def token_required(roles=None):
    """
    Decorator to require a valid token for a route
    
    Args:
        roles (list, optional): List of required roles
    
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = get_token_from_header()
            
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            token_info = validate_token(token)
            
            if not token_info or not token_info.get('active', False):
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check roles if specified
            if roles:
                user_roles = token_info.get('realm_access', {}).get('roles', [])
                if not any(role in user_roles for role in roles):
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Pass the token info to the route function
            return f(current_user=token_info, *args, **kwargs)
        
        return decorated_function
    
    return decorator

def hash_password(password):
    """
    Hash a password (not used with Keycloak, but kept for reference)
    
    Args:
        password (str): Password to hash
    
    Returns:
        str: Hashed password
    """
    import hashlib
    import os
    
    # Generate a random salt
    salt = os.urandom(32)
    
    # Hash the password with the salt
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    # Return the salt and key
    return salt + key

def verify_password(stored_password, provided_password):
    """
    Verify a password (not used with Keycloak, but kept for reference)
    
    Args:
        stored_password (bytes): Stored password hash
        provided_password (str): Password to verify
    
    Returns:
        bool: True if password matches
    """
    import hashlib
    
    # Extract the salt from the stored password
    salt = stored_password[:32]
    
    # Extract the key from the stored password
    stored_key = stored_password[32:]
    
    # Hash the provided password with the salt
    key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        salt,
        100000
    )
    
    # Compare the keys
    return key == stored_key