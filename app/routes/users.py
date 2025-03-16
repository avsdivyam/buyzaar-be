from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.services.keycloak import KeycloakService
from app.utils.security import token_required

bp = Blueprint('users', __name__)

@bp.route('/', methods=['GET'])
@token_required(roles=['admin'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    users = User.query.paginate(page=page, per_page=per_page)
    
    result = {
        'items': [{
            'id': user.id,
            'keycloak_id': user.keycloak_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        } for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'page': page
    }
    
    return jsonify(result), 200

@bp.route('/<int:id>', methods=['GET'])
@token_required()
def get_user(id, current_user):
    user = User.query.get_or_404(id)
    
    # Regular users can only view their own profile
    # Admins can view any profile
    if 'admin' not in current_user.get('roles', []):
        db_user = User.query.filter_by(keycloak_id=current_user['sub']).first_or_404()
        if user.id != db_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    result = {
        'id': user.id,
        'keycloak_id': user.keycloak_id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }
    
    return jsonify(result), 200

@bp.route('/me', methods=['GET'])
@token_required()
def get_current_user(current_user):
    user = User.query.filter_by(keycloak_id=current_user['sub']).first_or_404()
    
    result = {
        'id': user.id,
        'keycloak_id': user.keycloak_id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }
    
    return jsonify(result), 200

@bp.route('/me', methods=['PUT'])
@token_required()
def update_current_user(current_user):
    user = User.query.filter_by(keycloak_id=current_user['sub']).first_or_404()
    data = request.get_json()
    
    # Update user in database
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    db.session.commit()
    
    # Update user in Keycloak if needed
    keycloak_updates = {}
    if 'first_name' in data:
        keycloak_updates['firstName'] = data['first_name']
    if 'last_name' in data:
        keycloak_updates['lastName'] = data['last_name']
    
    if keycloak_updates:
        keycloak_service = KeycloakService()
        keycloak_service.update_user(user.keycloak_id, keycloak_updates)
    
    result = {
        'id': user.id,
        'keycloak_id': user.keycloak_id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }
    
    return jsonify(result), 200