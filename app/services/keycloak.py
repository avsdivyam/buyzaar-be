from flask import current_app
from keycloak import KeycloakOpenID, KeycloakAdmin
from app import db
from app.models import User

class KeycloakService:
    def __init__(self):
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
        Authenticate a user with Keycloak
        """
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
        
        return token
    
    def logout(self, refresh_token):
        """
        Logout a user from Keycloak
        """
        self.keycloak_openid.logout(refresh_token)
    
    def refresh_token(self, refresh_token):
        """
        Refresh an access token
        """
        return self.keycloak_openid.refresh_token(refresh_token)
    
    def register_user(self, email, password, first_name, last_name):
        """
        Register a new user in Keycloak
        """
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
    
    def update_user(self, user_id, user_data):
        """
        Update a user in Keycloak
        """
        self.keycloak_admin.update_user(user_id, user_data)
    
    def get_user_roles(self, token):
        """
        Get user roles from token
        """
        token_info = self.keycloak_openid.introspect(token)
        return token_info.get('realm_access', {}).get('roles', [])