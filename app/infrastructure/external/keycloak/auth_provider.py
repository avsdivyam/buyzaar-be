"""
Keycloak authentication provider module.

This module provides an authentication provider using Keycloak.
"""
from typing import Dict, Any, Optional, Tuple

from app.infrastructure.external.keycloak.client import KeycloakClient
from app.domain.exceptions import AuthenticationError, ValidationError


class KeycloakAuthProvider:
    """Authentication provider using Keycloak."""
    
    def __init__(self):
        """Initialize Keycloak authentication provider."""
        self.client = KeycloakClient()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user.
        
        Args:
            username: User's email or username
            password: User's password
            
        Returns:
            Dict[str, Any]: Authentication tokens and user info
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Get token from Keycloak
            token_response = self.client.login(username, password)
            
            # Get user info
            userinfo = self.client.get_userinfo(token_response['access_token'])
            
            # Add user info to token response
            token_response['user'] = {
                'id': userinfo['sub'],
                'email': userinfo['email'],
                'first_name': userinfo.get('given_name', ''),
                'last_name': userinfo.get('family_name', ''),
                'roles': self.client.get_user_roles(token_response['access_token'])
            }
            
            return token_response
        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")
    
    def logout(self, refresh_token: str) -> None:
        """
        Logout a user.
        
        Args:
            refresh_token: Refresh token
            
        Raises:
            AuthenticationError: If logout fails
        """
        try:
            self.client.logout(refresh_token)
        except Exception as e:
            raise AuthenticationError(f"Logout failed: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict[str, Any]: New authentication tokens
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        try:
            token_response = self.client.refresh_token(refresh_token)
            
            # Add user roles to token response
            token_response['roles'] = self.client.get_user_roles(token_response['access_token'])
            
            return token_response
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Dict[str, Any]: Token info or empty dict if invalid
        """
        try:
            token_info = self.client.validate_token(token)
            if not token_info or not token_info.get('active', False):
                return {}
            return token_info
        except Exception:
            return {}
    
    def register_user(self, email: str, password: str, first_name: str, last_name: str) -> str:
        """
        Register a new user.
        
        Args:
            email: User's email
            password: User's password
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            str: User ID
            
        Raises:
            ValidationError: If validation fails
            AuthenticationError: If registration fails
        """
        try:
            # Validate password
            self._validate_password(password)
            
            # Create user in Keycloak
            user_id = self.client.create_user({
                'email': email,
                'username': email,
                'firstName': first_name,
                'lastName': last_name,
                'enabled': True,
                'emailVerified': True,
                'credentials': [{
                    'type': 'password',
                    'value': password,
                    'temporary': False
                }]
            })
            
            return user_id
        except ValidationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"User registration failed: {str(e)}")
    
    def _validate_password(self, password: str) -> None:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Raises:
            ValidationError: If password is too weak
        """
        errors = []
        
        # Check length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # Check for uppercase letter
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letter
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digit
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if errors:
            raise ValidationError({'password': errors})