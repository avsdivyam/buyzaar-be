from flask import Blueprint, request, jsonify, current_app
from app.services.keycloak import KeycloakService
from app.utils.security import validate_token

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    keycloak_service = KeycloakService()
    
    try:
        token_info = keycloak_service.login(data['username'], data['password'])
        return jsonify(token_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@bp.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    
    if not data or 'refresh_token' not in data:
        return jsonify({'error': 'Refresh token is required'}), 400
    
    keycloak_service = KeycloakService()
    
    try:
        keycloak_service.logout(data['refresh_token'])
        return jsonify({'message': 'Successfully logged out'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    
    if not data or 'refresh_token' not in data:
        return jsonify({'error': 'Refresh token is required'}), 400
    
    keycloak_service = KeycloakService()
    
    try:
        token_info = keycloak_service.refresh_token(data['refresh_token'])
        return jsonify(token_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    keycloak_service = KeycloakService()
    
    try:
        user_id = keycloak_service.register_user(
            data['email'],
            data['password'],
            data['first_name'],
            data['last_name']
        )
        return jsonify({'user_id': user_id, 'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400