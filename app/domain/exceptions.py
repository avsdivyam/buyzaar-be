"""
Domain exceptions module.

This module defines domain-specific exceptions.
"""

class DomainError(Exception):
    """Base exception for all domain errors."""
    
    def __init__(self, message="A domain error occurred"):
        self.message = message
        super().__init__(self.message)


class ValidationError(DomainError):
    """Exception raised for domain validation errors."""
    
    def __init__(self, errors=None, message="Validation error"):
        self.errors = errors or {}
        super().__init__(message)


class NotFoundError(DomainError):
    """Exception raised when a domain entity is not found."""
    
    def __init__(self, entity_type="Entity", entity_id=None):
        message = f"{entity_type} not found"
        if entity_id is not None:
            message = f"{entity_type} with ID {entity_id} not found"
        super().__init__(message)


class BusinessRuleError(DomainError):
    """Exception raised when a business rule is violated."""
    
    def __init__(self, rule="", message="Business rule violation"):
        if rule:
            message = f"Business rule violation: {rule}"
        super().__init__(message)


class InsufficientInventoryError(BusinessRuleError):
    """Exception raised when product inventory is insufficient."""
    
    def __init__(self, product_id=None, product_name=None, requested=0, available=0):
        message = "Insufficient inventory"
        if product_name:
            message = f"Insufficient inventory for product '{product_name}'"
        elif product_id:
            message = f"Insufficient inventory for product ID {product_id}"
        
        if requested and available:
            message += f" (requested: {requested}, available: {available})"
            
        super().__init__(message=message)


class InvalidStatusTransitionError(BusinessRuleError):
    """Exception raised when an invalid status transition is attempted."""
    
    def __init__(self, entity_type="Entity", current_status=None, new_status=None):
        message = f"Invalid status transition for {entity_type}"
        if current_status and new_status:
            message = f"Invalid status transition for {entity_type} from '{current_status}' to '{new_status}'"
        super().__init__(message=message)


class AuthorizationError(DomainError):
    """Exception raised for domain authorization errors."""
    
    def __init__(self, message="Not authorized to perform this operation"):
        super().__init__(message)