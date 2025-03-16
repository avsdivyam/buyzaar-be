"""
Refresh token use case module.

This module defines the refresh token use case.
"""
from typing import Dict, Any

from app.domain.exceptions import ValidationError, AuthenticationError
from app.infrastructure.external.keycloak.auth_provider import KeycloakAuthProvider


class RefreshTokenUseCase:
    """Use case for refreshing authentication tokens."""
    
    def __init__(self, auth_provider: KeycloakAuthProvider):
        """
        Initialize refresh token use case.
        
        Args:
            auth_provider: Authentication provider
        """
        self.auth_provider = auth_provider
    
    def execute(self, refresh_token: str) -> Dict[str, Any]:
        """
        Execute the refresh token use case.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict[str, Any]: New authentication tokens
            
        Raises:
            ValidationError: If validation fails
            AuthenticationError: If token refresh fails
        """
        # Validate input
        if not refresh_token:
            raise ValidationError({'refresh_token': ['Refresh token is required']})
        
        # Refresh token with Keycloak
        return self.auth_provider.refresh_token(refresh_token)