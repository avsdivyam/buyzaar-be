"""
Login use case module.

This module defines the login use case.
"""
from typing import Dict, Any

from app.domain.models.user import User
from app.domain.exceptions import AuthenticationError, ValidationError
from app.infrastructure.external.keycloak.auth_provider import KeycloakAuthProvider
from app.infrastructure.database.repositories.user_repository import UserRepository


class LoginUseCase:
    """Use case for user login."""
    
    def __init__(self, auth_provider: KeycloakAuthProvider, user_repository: UserRepository):
        """
        Initialize login use case.
        
        Args:
            auth_provider: Authentication provider
            user_repository: User repository
        """
        self.auth_provider = auth_provider
        self.user_repository = user_repository
    
    def execute(self, username: str, password: str) -> Dict[str, Any]:
        """
        Execute the login use case.
        
        Args:
            username: User's email or username
            password: User's password
            
        Returns:
            Dict[str, Any]: Authentication tokens and user info
            
        Raises:
            ValidationError: If validation fails
            AuthenticationError: If authentication fails
        """
        # Validate input
        if not username or not password:
            raise ValidationError({'username': ['Username is required'], 'password': ['Password is required']})
        
        # Authenticate with Keycloak
        token_info = self.auth_provider.login(username, password)
        
        # Get user info from token
        user_info = token_info.get('user', {})
        keycloak_id = user_info.get('id')
        
        if not keycloak_id:
            raise AuthenticationError("Failed to get user information")
        
        # Check if user exists in our database
        try:
            user = self.user_repository.get_by_keycloak_id(keycloak_id)
        except:
            # If not, create the user
            user = User(
                keycloak_id=keycloak_id,
                email=user_info.get('email', ''),
                first_name=user_info.get('first_name', ''),
                last_name=user_info.get('last_name', '')
            )
            user = self.user_repository.create(user)
        
        # Add user ID to token info
        token_info['user']['db_id'] = user.id
        
        return token_info