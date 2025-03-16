"""
Common validators module.

This module provides common validation functions used throughout the application.
"""
import re
from typing import Optional, Dict, Any, List, Union


def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Dict[str, Any]: Validation result with 'valid' flag and 'errors' list
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
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Dict[str, Any]: Validation result with 'valid' flag and 'errors' dict
    """
    errors = {}
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors[field] = "This field is required"
        elif isinstance(data[field], str) and not data[field].strip():
            errors[field] = "This field cannot be empty"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_string_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> Dict[str, Any]:
    """
    Validate string length.
    
    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length (None for no maximum)
        
    Returns:
        Dict[str, Any]: Validation result with 'valid' flag and 'error' message
    """
    if not isinstance(value, str):
        return {'valid': False, 'error': "Value must be a string"}
    
    if len(value) < min_length:
        return {'valid': False, 'error': f"Value must be at least {min_length} characters long"}
    
    if max_length is not None and len(value) > max_length:
        return {'valid': False, 'error': f"Value cannot exceed {max_length} characters"}
    
    return {'valid': True, 'error': None}


def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                          max_value: Optional[Union[int, float]] = None) -> Dict[str, Any]:
    """
    Validate numeric value range.
    
    Args:
        value: Numeric value to validate
        min_value: Minimum allowed value (None for no minimum)
        max_value: Maximum allowed value (None for no maximum)
        
    Returns:
        Dict[str, Any]: Validation result with 'valid' flag and 'error' message
    """
    if not isinstance(value, (int, float)):
        return {'valid': False, 'error': "Value must be a number"}
    
    if min_value is not None and value < min_value:
        return {'valid': False, 'error': f"Value must be at least {min_value}"}
    
    if max_value is not None and value > max_value:
        return {'valid': False, 'error': f"Value cannot exceed {max_value}"}
    
    return {'valid': True, 'error': None}