"""
Authentication middleware.

This module provides middleware for authentication and authorization.
"""
from functools import wraps
from flask import request, jsonify, current_app, g
from typing import List, Optional, Callable

from app.infrastructure.external.keycloak.auth_provider import KeycloakAuthProvider
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.core.security import get_token_from_header


def token_required(roles: Optional[List[str]] = None) -> Callable:
    """
    Decorator to require a valid token for a route.
    
    Args:
        roles: List of required roles
    
    Returns:
        Callable: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = get_token_from_header()
            
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            try:
                # Validate token
                auth_provider = KeycloakAuthProvider()
                token_info = auth_provider.validate_token(token)
                
                if not token_info or not token_info.get('active', False):
                    return jsonify({'error': 'Invalid or expired token'}), 401
                
                # Check roles if specified
                if roles:
                    user_roles = token_info.get('realm_access', {}).get('roles', [])
                    if not any(role in user_roles for role in roles):
                        return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Get user from database
                user_repository = UserRepository()
                try:
                    user = user_repository.get_by_keycloak_id(token_info['sub'])
                    # Store user in Flask's g object for access in the route
                    g.user = user
                except Exception as e:
                    current_app.logger.error(f"Error getting user: {str(e)}")
                    # Continue even if user not found in database
                
                # Store token info in Flask's g object for access in the route
                g.token_info = token_info
                
                # Pass the token info to the route function
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Token validation error: {str(e)}")
                return jsonify({'error': 'Authentication error'}), 401
        
        return decorated_function
    
    return decorator