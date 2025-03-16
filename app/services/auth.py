"""
Authentication service.
"""
from flask import current_app
from keycloak import KeycloakOpenID, KeycloakAdmin
from app import db
from app.models import User
from app.core.exceptions import AuthenticationError

class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        """Initialize the authentication service."""
        self.server_url = current_app.config['KEYCLOAK_SERVER_URL']
        self.realm = current_app.config['KEYCLOAK_REALM']
        self.client_id = current_app.config['KEYCLOAK_CLIENT_ID']
        self.client_secret = current_app.config['KEYCLOAK_CLIENT_SECRET']
        
        # Initialize Keycloak OpenID client
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.realm,
            client_secret_key=self.client_secret
        )
        
        # Initialize Keycloak Admin client
        self.keycloak_admin = KeycloakAdmin(
            server_url=self.server_url,
            realm_name=self.realm,
            client_id=self.client_id,
            client_secret_key=self.client_secret,
            verify=True
        )
    
    def login(self, username, password):
        """
        Authenticate a user with Keycloak.
        
        Args:
            username (str): User's email or username
            password (str): User's password
            
        Returns:
            dict: Authentication tokens and user info
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Get token from Keycloak
            token = self.keycloak_openid.token(username, password)
            
            # Get user info
            userinfo = self.keycloak_openid.userinfo(token['access_token'])
            
            # Check if user exists in our database
            user = User.query.filter_by(keycloak_id=userinfo['sub']).first()
            
            # If not, create the user
            if not user:
                user = User(
                    keycloak_id=userinfo['sub'],
                    email=userinfo['email'],
                    first_name=userinfo.get('given_name', ''),
                    last_name=userinfo.get('family_name', '')
                )
                db.session.add(user)
                db.session.commit()
            
            # Add user info to token response
            token['user'] = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': self._get_user_roles(token['access_token'])
            }
            
            return token
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            raise AuthenticationError("Invalid username or password")
    
    def logout(self, refresh_token):
        """
        Logout a user from Keycloak.
        
        Args:
            refresh_token (str): Refresh token
            
        Raises:
            AuthenticationError: If logout fails
        """
        try:
            self.keycloak_openid.logout(refresh_token)
        except Exception as e:
            current_app.logger.error(f"Logout error: {str(e)}")
            raise AuthenticationError("Logout failed")
    
    def refresh_token(self, refresh_token):
        """
        Refresh an access token.
        
        Args:
            refresh_token (str): Refresh token
            
        Returns:
            dict: New authentication tokens
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        try:
            token = self.keycloak_openid.refresh_token(refresh_token)
            
            # Add user roles to token response
            token['roles'] = self._get_user_roles(token['access_token'])
            
            return token
        except Exception as e:
            current_app.logger.error(f"Token refresh error: {str(e)}")
            raise AuthenticationError("Invalid or expired refresh token")
    
    def register_user(self, email, password, first_name, last_name):
        """
        Register a new user in Keycloak.
        
        Args:
            email (str): User's email
            password (str): User's password
            first_name (str): User's first name
            last_name (str): User's last name
            
        Returns:
            str: User ID
            
        Raises:
            AuthenticationError: If registration fails
        """
        try:
            # Create user in Keycloak
            user_id = self.keycloak_admin.create_user({
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
            
            # Create user in our database
            user = User(
                keycloak_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            db.session.add(user)
            db.session.commit()
            
            return user_id
        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            raise AuthenticationError("User registration failed")
    
    def validate_token(self, token):
        """
        Validate a JWT token with Keycloak.
        
        Args:
            token (str): JWT token
            
        Returns:
            dict: Token info or None if invalid
        """
        try:
            return self.keycloak_openid.introspect(token)
        except Exception as e:
            current_app.logger.error(f"Token validation error: {str(e)}")
            return None
    
    def _get_user_roles(self, token):
        """
        Get user roles from token.
        
        Args:
            token (str): JWT token
            
        Returns:
            list: User roles
        """
        try:
            token_info = self.keycloak_openid.introspect(token)
            return token_info.get('realm_access', {}).get('roles', [])
        except Exception:
            return []