"""
Authentication API endpoints.
"""
from flask import request, jsonify, current_app
from app.api import api_bp
from app.services.auth import AuthService
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.schemas import LoginSchema, RegisterSchema

@api_bp.route('/v1/auth/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Returns:
        JSON: Authentication tokens and user info
    """
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.get_json())
        
        # Authenticate user
        auth_service = AuthService()
        token_info = auth_service.login(data['username'], data['password'])
        
        return jsonify(token_info), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/auth/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.
    
    Returns:
        JSON: Success message
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data or 'refresh_token' not in data:
            raise ValidationError({'refresh_token': ['Refresh token is required']})
        
        # Logout user
        auth_service = AuthService()
        auth_service.logout(data['refresh_token'])
        
        return jsonify({'message': 'Successfully logged out'}), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/auth/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh token endpoint.
    
    Returns:
        JSON: New authentication tokens
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data or 'refresh_token' not in data:
            raise ValidationError({'refresh_token': ['Refresh token is required']})
        
        # Refresh token
        auth_service = AuthService()
        token_info = auth_service.refresh_token(data['refresh_token'])
        
        return jsonify(token_info), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/auth/register', methods=['POST'])
def register():
    """
    User registration endpoint.
    
    Returns:
        JSON: User ID and success message
    """
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.get_json())
        
        # Register user
        auth_service = AuthService()
        user_id = auth_service.register_user(
            data['email'],
            data['password'],
            data['first_name'],
            data['last_name']
        )
        
        return jsonify({
            'user_id': user_id,
            'message': 'User registered successfully'
        }), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500