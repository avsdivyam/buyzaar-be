"""
Custom exceptions for the application.
"""

class AppError(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message="An error occurred"):
        self.message = message
        super().__init__(self.message)


class ValidationError(AppError):
    """Exception raised for validation errors."""
    
    def __init__(self, errors=None, message="Validation error"):
        self.errors = errors or {}
        super().__init__(message)


class NotFoundError(AppError):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message="Resource not found"):
        super().__init__(message)


class AuthenticationError(AppError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message="Authentication failed"):
        super().__init__(message)


class AuthorizationError(AppError):
    """Exception raised for authorization errors."""
    
    def __init__(self, message="Not authorized"):
        super().__init__(message)


class BusinessLogicError(AppError):
    """Exception raised for business logic errors."""
    
    def __init__(self, message="Business logic error"):
        super().__init__(message)


class ExternalServiceError(AppError):
    """Exception raised for errors in external services."""
    
    def __init__(self, service=None, message="External service error"):
        self.service = service
        if service:
            message = f"{service} service error: {message}"
        super().__init__(message)