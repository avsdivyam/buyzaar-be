"""
Keycloak client module.

This module provides a client for interacting with Keycloak API.
"""
from flask import current_app
from keycloak import KeycloakOpenID, KeycloakAdmin
from typing import Dict, Any, Optional, List

class KeycloakClient:
    """Client for interacting with Keycloak API."""
    
    def __init__(self):
        """Initialize Keycloak client."""
        self.server_url = current_app.config['KEYCLOAK_SERVER_URL']
        self.realm = current_app.config['KEYCLOAK_REALM']
        self.client_id = current_app.config['KEYCLOAK_CLIENT_ID']
        self.client_secret = current_app.config['KEYCLOAK_CLIENT_SECRET']
        
        # Initialize Keycloak OpenID client for authentication
        self.openid_client = KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.realm,
            client_secret_key=self.client_secret
        )
        
        # Initialize Keycloak Admin client for user management
        self.admin_client = KeycloakAdmin(
            server_url=self.server_url,
            realm_name=self.realm,
            client_id=self.client_id,
            client_secret_key=self.client_secret,
            verify=True
        )
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with Keycloak.
        
        Args:
            username: User's email or username
            password: User's password
            
        Returns:
            Dict[str, Any]: Authentication tokens and user info
            
        Raises:
            Exception: If authentication fails
        """
        return self.openid_client.token(username, password)
    
    def logout(self, refresh_token: str) -> None:
        """
        Logout a user from Keycloak.
        
        Args:
            refresh_token: Refresh token
            
        Raises:
            Exception: If logout fails
        """
        self.openid_client.logout(refresh_token)
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict[str, Any]: New authentication tokens
            
        Raises:
            Exception: If token refresh fails
        """
        return self.openid_client.refresh_token(refresh_token)
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a JWT token with Keycloak.
        
        Args:
            token: JWT token
            
        Returns:
            Dict[str, Any]: Token info or empty dict if invalid
            
        Raises:
            Exception: If token validation fails
        """
        try:
            return self.openid_client.introspect(token)
        except Exception:
            return {}
    
    def get_userinfo(self, token: str) -> Dict[str, Any]:
        """
        Get user info from Keycloak.
        
        Args:
            token: Access token
            
        Returns:
            Dict[str, Any]: User info
            
        Raises:
            Exception: If getting user info fails
        """
        return self.openid_client.userinfo(token)
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user in Keycloak.
        
        Args:
            user_data: User data including email, username, firstName, lastName, and credentials
            
        Returns:
            str: User ID
            
        Raises:
            Exception: If user creation fails
        """
        return self.admin_client.create_user(user_data)
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user from Keycloak.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: User data
            
        Raises:
            Exception: If getting user fails
        """
        return self.admin_client.get_user(user_id)
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> None:
        """
        Update a user in Keycloak.
        
        Args:
            user_id: User ID
            user_data: User data to update
            
        Raises:
            Exception: If user update fails
        """
        self.admin_client.update_user(user_id, user_data)
    
    def delete_user(self, user_id: str) -> None:
        """
        Delete a user from Keycloak.
        
        Args:
            user_id: User ID
            
        Raises:
            Exception: If user deletion fails
        """
        self.admin_client.delete_user(user_id)
    
    def get_user_roles(self, token: str) -> List[str]:
        """
        Get user roles from token.
        
        Args:
            token: JWT token
            
        Returns:
            List[str]: User roles
        """
        token_info = self.validate_token(token)
        return token_info.get('realm_access', {}).get('roles', [])
    
    def assign_role(self, user_id: str, role_name: str) -> None:
        """
        Assign a role to a user.
        
        Args:
            user_id: User ID
            role_name: Role name
            
        Raises:
            Exception: If role assignment fails
        """
        role = self.admin_client.get_realm_role(role_name)
        self.admin_client.assign_realm_roles(user_id, [role])