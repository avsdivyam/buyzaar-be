"""
Address value object.

This module defines the Address value object for representing physical addresses.
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class Address:
    """
    Address value object representing a physical address.
    
    This is an immutable value object that represents a physical address
    with street, city, state, postal code, and country.
    """
    
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    
    def __str__(self) -> str:
        """String representation of Address."""
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Address to dictionary.
        
        Returns:
            Dict[str, Any]: Address as dictionary
        """
        return {
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """
        Create an Address from a dictionary.
        
        Args:
            data: Dictionary with address attributes
            
        Returns:
            Address: Address instance
        """
        return cls(
            street=data.get('street', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            postal_code=data.get('postal_code', ''),
            country=data.get('country', '')
        )