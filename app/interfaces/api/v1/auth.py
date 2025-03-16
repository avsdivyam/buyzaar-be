"""
Authentication API endpoints.

This module defines the authentication API endpoints.
"""
from flask import request, jsonify, current_app
from app.interfaces.api import api_bp
from app.interfaces.serializers.auth import LoginSchema, RegisterSchema
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.register import RegisterUseCase
from app.application.use_cases.auth.logout import LogoutUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.infrastructure.external.keycloak.auth_provider import KeycloakAuthProvider
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.domain.exceptions import ValidationError, AuthenticationError


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
        data = schema.load(request.get_json() or {})
        
        # Create dependencies
        auth_provider = KeycloakAuthProvider()
        user_repository = UserRepository()
        
        # Create and execute use case
        use_case = LoginUseCase(auth_provider, user_repository)
        result = use_case.execute(data['username'], data['password'])
        
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@api_bp.route('/v1/auth/register', methods=['POST'])
def register():
    """
    User registration endpoint.
    
    Returns:
        JSON: Registration result with user ID
    """
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.get_json() or {})
        
        # Create dependencies
        auth_provider = KeycloakAuthProvider()
        user_repository = UserRepository()
        
        # Create and execute use case
        use_case = RegisterUseCase(auth_provider, user_repository)
        result = use_case.execute(
            data['email'],
            data['password'],
            data['first_name'],
            data['last_name']
        )
        
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@api_bp.route('/v1/auth/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.
    
    Returns:
        JSON: Success message
    """
    try:
        # Get request data
        data = request.get_json() or {}
        
        # Create dependencies
        auth_provider = KeycloakAuthProvider()
        
        # Create and execute use case
        use_case = LogoutUseCase(auth_provider)
        use_case.execute(data.get('refresh_token', ''))
        
        return jsonify({'message': 'Successfully logged out'}), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 400
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
        # Get request data
        data = request.get_json() or {}
        
        # Create dependencies
        auth_provider = KeycloakAuthProvider()
        
        # Create and execute use case
        use_case = RefreshTokenUseCase(auth_provider)
        result = use_case.execute(data.get('refresh_token', ''))
        
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500