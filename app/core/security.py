"""
Security utilities module.

This module provides utilities for security-related operations.
"""
import os
import hashlib
import secrets
from typing import Optional, Dict, Any, Tuple
from flask import request, current_app


def get_token_from_header() -> Optional[str]:
    """
    Extract token from Authorization header.
    
    Returns:
        Optional[str]: Token or None if not found
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    return auth_header.split(' ')[1]


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Length of the token in bytes
        
    Returns:
        str: Secure token as a hexadecimal string
    """
    return secrets.token_hex(length)


def hash_password(password: str) -> Tuple[bytes, bytes]:
    """
    Hash a password with a random salt using PBKDF2.
    
    Args:
        password: Password to hash
        
    Returns:
        Tuple[bytes, bytes]: (salt, hashed_password)
    """
    # Generate a random salt
    salt = os.urandom(32)
    
    # Hash the password with the salt
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Number of iterations
    )
    
    return salt, hashed_password


def verify_password(stored_salt: bytes, stored_hash: bytes, provided_password: str) -> bool:
    """
    Verify a password against a stored hash.
    
    Args:
        stored_salt: Stored salt
        stored_hash: Stored password hash
        provided_password: Password to verify
        
    Returns:
        bool: True if password matches
    """
    # Hash the provided password with the stored salt
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        stored_salt,
        100000  # Number of iterations
    )
    
    # Compare the hashes using a constant-time comparison
    return secrets.compare_digest(stored_hash, hashed_password)


def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data to prevent injection attacks.
    
    Args:
        data: Input data dictionary
        
    Returns:
        Dict[str, Any]: Sanitized data
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Basic sanitization - remove control characters
            sanitized[key] = ''.join(c for c in value if ord(c) >= 32)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_input(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized