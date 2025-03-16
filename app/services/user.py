"""
User service.
"""
from sqlalchemy import or_
from app import db
from app.models import User
from app.core.exceptions import NotFoundError
from app.services.auth import AuthService

class UserService:
    """Service for user operations."""
    
    def get_users_query(self, search=''):
        """
        Get users query with filters.
        
        Args:
            search (str): Search term for email, first name, and last name
            
        Returns:
            Query: SQLAlchemy query object
        """
        # Start with base query for active users
        query = User.query.filter_by(is_active=True)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
            )
        
        # Order by created_at desc
        query = query.order_by(User.created_at.desc())
        
        return query
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID.
        
        Args:
            user_id (int): User ID
            
        Returns:
            User: User object
            
        Raises:
            NotFoundError: If user not found
        """
        user = User.query.filter_by(id=user_id, is_active=True).first()
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user
    
    def get_user_by_keycloak_id(self, keycloak_id):
        """
        Get user by Keycloak ID.
        
        Args:
            keycloak_id (str): Keycloak user ID
            
        Returns:
            User: User object
            
        Raises:
            NotFoundError: If user not found
        """
        user = User.query.filter_by(keycloak_id=keycloak_id, is_active=True).first()
        if not user:
            raise NotFoundError(f"User with Keycloak ID {keycloak_id} not found")
        return user
    
    def get_user_by_email(self, email):
        """
        Get user by email.
        
        Args:
            email (str): User email
            
        Returns:
            User: User object or None if not found
        """
        return User.query.filter_by(email=email, is_active=True).first()
    
    def update_user_by_keycloak_id(self, keycloak_id, user_data):
        """
        Update a user by Keycloak ID.
        
        Args:
            keycloak_id (str): Keycloak user ID
            user_data (dict): User data
            
        Returns:
            User: Updated user
            
        Raises:
            NotFoundError: If user not found
        """
        user = self.get_user_by_keycloak_id(keycloak_id)
        
        # Update user attributes
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        
        # Update user in Keycloak if needed
        keycloak_updates = {}
        if 'first_name' in user_data:
            keycloak_updates['firstName'] = user_data['first_name']
        if 'last_name' in user_data:
            keycloak_updates['lastName'] = user_data['last_name']
        
        if keycloak_updates:
            auth_service = AuthService()
            auth_service.keycloak_admin.update_user(keycloak_id, keycloak_updates)
        
        return user
    
    def deactivate_user(self, user_id):
        """
        Deactivate a user (soft delete).
        
        Args:
            user_id (int): User ID
            
        Raises:
            NotFoundError: If user not found
        """
        user = self.get_user_by_id(user_id)
        
        # Soft delete
        user.is_active = False
        db.session.commit()
        
        # Disable user in Keycloak
        auth_service = AuthService()
        auth_service.keycloak_admin.update_user(user.keycloak_id, {'enabled': False})
        
        return True