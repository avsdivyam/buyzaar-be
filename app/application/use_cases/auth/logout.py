"""
Logout use case module.

This module defines the logout use case.
"""
from app.domain.exceptions import ValidationError, AuthenticationError
from app.infrastructure.external.keycloak.auth_provider import KeycloakAuthProvider


class LogoutUseCase:
    """Use case for user logout."""
    
    def __init__(self, auth_provider: KeycloakAuthProvider):
        """
        Initialize logout use case.
        
        Args:
            auth_provider: Authentication provider
        """
        self.auth_provider = auth_provider
    
    def execute(self, refresh_token: str) -> None:
        """
        Execute the logout use case.
        
        Args:
            refresh_token: Refresh token
            
        Raises:
            ValidationError: If validation fails
            AuthenticationError: If logout fails
        """
        # Validate input
        if not refresh_token:
            raise ValidationError({'refresh_token': ['Refresh token is required']})
        
        # Logout from Keycloak
        self.auth_provider.logout(refresh_token)