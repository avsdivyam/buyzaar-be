"""
Decorators for the application.
"""
from functools import wraps
from flask import request, jsonify, current_app
from app.services.auth import AuthService
from app.core.exceptions import AuthenticationError, AuthorizationError

def token_required(roles=None):
    """
    Decorator to require a valid token for a route.
    
    Args:
        roles (list, optional): List of required roles
    
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = _get_token_from_header()
            
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            try:
                auth_service = AuthService()
                token_info = auth_service.validate_token(token)
                
                if not token_info or not token_info.get('active', False):
                    raise AuthenticationError("Invalid or expired token")
                
                # Check roles if specified
                if roles:
                    user_roles = token_info.get('realm_access', {}).get('roles', [])
                    if not any(role in user_roles for role in roles):
                        raise AuthorizationError("Insufficient permissions")
                
                # Pass the token info to the route function
                return f(current_user=token_info, *args, **kwargs)
            except AuthenticationError:
                return jsonify({'error': 'Invalid or expired token'}), 401
            except AuthorizationError:
                return jsonify({'error': 'Insufficient permissions'}), 403
            except Exception as e:
                current_app.logger.error(f"Token validation error: {str(e)}")
                return jsonify({'error': 'Authentication error'}), 401
        
        return decorated_function
    
    return decorator

def _get_token_from_header():
    """
    Extract token from Authorization header.
    
    Returns:
        str: Token or None
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    return auth_header.split(' ')[1]