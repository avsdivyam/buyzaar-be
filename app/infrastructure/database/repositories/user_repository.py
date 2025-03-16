"""
User repository implementation.

This module implements the user repository using SQLAlchemy ORM.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import or_

from app import db
from app.domain.models.user import User
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models.user import UserModel


class UserRepository:
    """Repository for User domain model using SQLAlchemy ORM."""
    
    def get_by_id(self, user_id: int) -> User:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User: User domain model
            
        Raises:
            NotFoundError: If user not found
        """
        user_model = UserModel.query.get(user_id)
        if not user_model:
            raise NotFoundError(entity_type="User", entity_id=user_id)
        
        return self._to_domain(user_model)
    
    def get_by_keycloak_id(self, keycloak_id: str) -> User:
        """
        Get a user by Keycloak ID.
        
        Args:
            keycloak_id: Keycloak user ID
            
        Returns:
            User: User domain model
            
        Raises:
            NotFoundError: If user not found
        """
        user_model = UserModel.query.filter_by(keycloak_id=keycloak_id).first()
        if not user_model:
            raise NotFoundError(entity_type="User", entity_id=keycloak_id)
        
        return self._to_domain(user_model)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: User email
            
        Returns:
            Optional[User]: User domain model or None if not found
        """
        user_model = UserModel.query.filter_by(email=email).first()
        if not user_model:
            return None
        
        return self._to_domain(user_model)
    
    def get_all(self, page: int = 1, per_page: int = 10, search: str = "") -> List[User]:
        """
        Get all users with optional pagination and search.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            search: Search term for email, first name, and last name
            
        Returns:
            List[User]: List of user domain models
        """
        query = UserModel.query
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    UserModel.email.ilike(search_term),
                    UserModel.first_name.ilike(search_term),
                    UserModel.last_name.ilike(search_term)
                )
            )
        
        # Apply pagination
        users = query.paginate(page=page, per_page=per_page)
        
        return [self._to_domain(user) for user in users.items]
    
    def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User domain model
            
        Returns:
            User: Created user with ID
        """
        user_model = UserModel(
            keycloak_id=user.keycloak_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )
        
        db.session.add(user_model)
        db.session.commit()
        
        # Update domain model with generated ID
        user.id = user_model.id
        
        return user
    
    def update(self, user: User) -> User:
        """
        Update an existing user.
        
        Args:
            user: User domain model
            
        Returns:
            User: Updated user
            
        Raises:
            NotFoundError: If user not found
        """
        user_model = UserModel.query.get(user.id)
        if not user_model:
            raise NotFoundError(entity_type="User", entity_id=user.id)
        
        # Update model attributes
        user_model.email = user.email
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name
        user_model.is_active = user.is_active
        
        db.session.commit()
        
        return user
    
    def delete(self, user_id: int) -> None:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Raises:
            NotFoundError: If user not found
        """
        user_model = UserModel.query.get(user_id)
        if not user_model:
            raise NotFoundError(entity_type="User", entity_id=user_id)
        
        db.session.delete(user_model)
        db.session.commit()
    
    def _to_domain(self, user_model: UserModel) -> User:
        """
        Convert ORM model to domain model.
        
        Args:
            user_model: SQLAlchemy user model
            
        Returns:
            User: User domain model
        """
        return User(
            id=user_model.id,
            keycloak_id=user_model.keycloak_id,
            email=user_model.email,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )