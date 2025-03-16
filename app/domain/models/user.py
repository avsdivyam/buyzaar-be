"""
User domain model.

This module defines the User domain model and related value objects.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.domain.exceptions import ValidationError
from app.core.validators import validate_email


@dataclass
class User:
    """User domain model representing a user in the system."""
    
    id: Optional[int] = None
    keycloak_id: Optional[str] = None
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Validate user attributes after initialization."""
        self.validate()
        
        # Set timestamps if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def validate(self) -> None:
        """
        Validate user attributes.
        
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Validate email
        if not self.email:
            errors['email'] = "Email is required"
        elif not validate_email(self.email):
            errors['email'] = "Invalid email format"
        
        # Validate first name
        if not self.first_name:
            errors['first_name'] = "First name is required"
        
        # Validate last name
        if not self.last_name:
            errors['last_name'] = "Last name is required"
        
        if errors:
            raise ValidationError(errors)
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def update(self, data: Dict[str, Any]) -> None:
        """
        Update user attributes.
        
        Args:
            data: Dictionary of attributes to update
            
        Raises:
            ValidationError: If validation fails
        """
        # Update attributes
        if 'email' in data:
            self.email = data['email']
        if 'first_name' in data:
            self.first_name = data['first_name']
        if 'last_name' in data:
            self.last_name = data['last_name']
        if 'is_active' in data:
            self.is_active = data['is_active']
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
        
        # Validate updated attributes
        self.validate()
    
    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user to dictionary.
        
        Returns:
            Dict[str, Any]: User as dictionary
        """
        return {
            'id': self.id,
            'keycloak_id': self.keycloak_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User from a dictionary.
        
        Args:
            data: Dictionary with user attributes
            
        Returns:
            User: User instance
        """
        # Convert string timestamps to datetime objects if present
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get('id'),
            keycloak_id=data.get('keycloak_id'),
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_active=data.get('is_active', True),
            created_at=created_at,
            updated_at=updated_at
        )