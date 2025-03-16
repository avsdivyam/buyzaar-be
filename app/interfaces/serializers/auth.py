"""
Authentication serializers.

This module defines serializers for authentication requests and responses.
"""
from marshmallow import Schema, fields, validates, ValidationError
import re


class LoginSchema(Schema):
    """Schema for login requests."""
    
    username = fields.String(required=True)
    password = fields.String(required=True)


class RegisterSchema(Schema):
    """Schema for user registration requests."""
    
    email = fields.Email(required=True)
    password = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    
    @validates('password')
    def validate_password(self, value):
        """Validate password complexity."""
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not any(char.isdigit() for char in value):
            raise ValidationError('Password must contain at least one digit')
        
        if not any(char.isupper() for char in value):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        if not any(char.islower() for char in value):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError('Password must contain at least one special character')


class RefreshTokenSchema(Schema):
    """Schema for refresh token requests."""
    
    refresh_token = fields.String(required=True)