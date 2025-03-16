"""
Register use case module.

This module defines the register use case.
"""
from typing import Dict, Any

from app.domain.models.user import User
from app.domain.exceptions import ValidationError, AuthenticationError
from app.infrastructure.external.keycloak.auth_provider import KeycloakAuthProvider
from app.infrastructure.database.repositories.user_repository import UserRepository


class RegisterUseCase:
    """Use case for user registration."""
    
    def __init__(self, auth_provider: KeycloakAuthProvider, user_repository: UserRepository):
        """
        Initialize register use case.
        
        Args:
            auth_provider: Authentication provider
            user_repository: User repository
        """
        self.auth_provider = auth_provider
        self.user_repository = user_repository
    
    def execute(self, email: str, password: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """
        Execute the register use case.
        
        Args:
            email: User's email
            password: User's password
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            Dict[str, Any]: Registration result with user ID
            
        Raises:
            ValidationError: If validation fails
            AuthenticationError: If registration fails
        """
        # Validate input
        errors = {}
        
        if not email:
            errors['email'] = ['Email is required']
        
        if not password:
            errors['password'] = ['Password is required']
        
        if not first_name:
            errors['first_name'] = ['First name is required']
        
        if not last_name:
            errors['last_name'] = ['Last name is required']
        
        if errors:
            raise ValidationError(errors)
        
        # Check if user already exists
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValidationError({'email': ['Email already in use']})
        
        # Register user in Keycloak
        keycloak_id = self.auth_provider.register_user(email, password, first_name, last_name)
        
        # Create user in our database
        user = User(
            keycloak_id=keycloak_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user = self.user_repository.create(user)
        
        return {
            'id': user.id,
            'keycloak_id': keycloak_id,
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        }