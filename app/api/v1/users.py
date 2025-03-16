"""
User API endpoints.
"""
from flask import request, jsonify, current_app
from app.api import api_bp
from app.services.user import UserService
from app.core.decorators import token_required
from app.core.exceptions import ValidationError, NotFoundError
from app.core.schemas import UserSchema, UserUpdateSchema
from app.core.pagination import paginate

@api_bp.route('/v1/users', methods=['GET'])
@token_required(roles=['admin'])
def get_users(current_user):
    """
    Get users endpoint (admin only).
    
    Args:
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Paginated list of users
    """
    try:
        user_service = UserService()
        
        # Get query parameters
        search = request.args.get('search', '')
        
        # Get users query
        query = user_service.get_users_query(search=search)
        
        # Paginate results
        return paginate(query, UserSchema())
    except Exception as e:
        current_app.logger.error(f"Error getting users: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/users/<int:id>', methods=['GET'])
@token_required()
def get_user(id, current_user):
    """
    Get user by ID endpoint.
    
    Args:
        id (int): User ID
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: User details
    """
    try:
        # Check if user is authorized to view this profile
        is_admin = 'admin' in current_user.get('roles', [])
        user_service = UserService()
        
        # Regular users can only view their own profile
        if not is_admin:
            db_user = user_service.get_user_by_keycloak_id(current_user['sub'])
            if db_user.id != id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        user = user_service.get_user_by_id(id)
        
        schema = UserSchema()
        return jsonify(schema.dump(user)), 200
    except NotFoundError:
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting user {id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/users/me', methods=['GET'])
@token_required()
def get_current_user(current_user):
    """
    Get current user endpoint.
    
    Args:
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: User details
    """
    try:
        user_service = UserService()
        user = user_service.get_user_by_keycloak_id(current_user['sub'])
        
        schema = UserSchema()
        return jsonify(schema.dump(user)), 200
    except NotFoundError:
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting current user: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/users/me', methods=['PUT'])
@token_required()
def update_current_user(current_user):
    """
    Update current user endpoint.
    
    Args:
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Updated user details
    """
    try:
        # Validate request data
        schema = UserUpdateSchema()
        data = schema.load(request.get_json())
        
        # Update user
        user_service = UserService()
        user = user_service.update_user_by_keycloak_id(current_user['sub'], data)
        
        return jsonify(UserSchema().dump(user)), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except NotFoundError:
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating current user: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500