"""
Order domain model.

This module defines the Order domain model and related entities.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from app.domain.exceptions import ValidationError, BusinessRuleError, InvalidStatusTransitionError
from app.domain.value_objects.money import Money
from app.domain.value_objects.address import Address


class OrderStatus:
    """Order status constants."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    
    @classmethod
    def all(cls) -> List[str]:
        """Get all valid statuses."""
        return [cls.PENDING, cls.PROCESSING, cls.SHIPPED, cls.DELIVERED, cls.CANCELLED]
    
    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if a status is valid."""
        return status in cls.all()
    
    @classmethod
    def is_final(cls, status: str) -> bool:
        """Check if a status is final (cannot be changed)."""
        return status in [cls.DELIVERED, cls.CANCELLED]
    
    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """Check if a status transition is valid."""
        # Cannot transition from a final status
        if cls.is_final(from_status):
            return False
        
        # Cannot transition to the same status
        if from_status == to_status:
            return False
        
        # Define valid transitions
        valid_transitions = {
            cls.PENDING: [cls.PROCESSING, cls.CANCELLED],
            cls.PROCESSING: [cls.SHIPPED, cls.CANCELLED],
            cls.SHIPPED: [cls.DELIVERED, cls.CANCELLED]
        }
        
        return to_status in valid_transitions.get(from_status, [])


@dataclass
class OrderItem:
    """Order item entity representing a product in an order."""
    
    id: Optional[int] = None
    order_id: Optional[int] = None
    product_id: int = 0
    product_name: str = ""
    quantity: int = 0
    price: Money = None
    
    def __post_init__(self):
        """Initialize and validate order item."""
        # Initialize price if provided as number
        if self.price is None:
            self.price = Money(Decimal('0.00'))
        elif isinstance(self.price, (int, float, str, Decimal)):
            self.price = Money(Decimal(str(self.price)))
        
        self.validate()
    
    def validate(self) -> None:
        """
        Validate order item attributes.
        
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Validate product_id
        if not self.product_id:
            errors['product_id'] = "Product ID is required"
        
        # Validate quantity
        if self.quantity <= 0:
            errors['quantity'] = "Quantity must be greater than zero"
        
        # Validate price
        if self.price is None or self.price.amount <= 0:
            errors['price'] = "Price must be greater than zero"
        
        if errors:
            raise ValidationError(errors)
    
    @property
    def subtotal(self) -> Money:
        """Calculate subtotal for this item."""
        return self.price * self.quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert order item to dictionary.
        
        Returns:
            Dict[str, Any]: Order item as dictionary
        """
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': float(self.price.amount) if self.price else None,
            'subtotal': float(self.subtotal.amount) if self.price else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderItem':
        """
        Create an OrderItem from a dictionary.
        
        Args:
            data: Dictionary with order item attributes
            
        Returns:
            OrderItem: OrderItem instance
        """
        # Convert price to Money object
        price = data.get('price')
        if price is not None and not isinstance(price, Money):
            price = Money(Decimal(str(price)))
        
        return cls(
            id=data.get('id'),
            order_id=data.get('order_id'),
            product_id=data.get('product_id', 0),
            product_name=data.get('product_name', ''),
            quantity=data.get('quantity', 0),
            price=price
        )


@dataclass
class Order:
    """Order domain model representing an order in the system."""
    
    id: Optional[int] = None
    user_id: int = 0
    status: str = OrderStatus.PENDING
    total_amount: Money = None
    shipping_address: Optional[Address] = None
    tracking_number: Optional[str] = None
    notes: str = ""
    items: List[OrderItem] = field(default_factory=list)
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize and validate order."""
        # Initialize total_amount if provided as number
        if self.total_amount is None:
            self.total_amount = Money(Decimal('0.00'))
        elif isinstance(self.total_amount, (int, float, str, Decimal)):
            self.total_amount = Money(Decimal(str(self.total_amount)))
        
        # Initialize shipping_address if provided as dict
        if isinstance(self.shipping_address, dict):
            self.shipping_address = Address.from_dict(self.shipping_address)
        
        self.validate()
        
        # Set timestamps if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def validate(self) -> None:
        """
        Validate order attributes.
        
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Validate user_id
        if not self.user_id:
            errors['user_id'] = "User ID is required"
        
        # Validate status
        if not self.status or not OrderStatus.is_valid(self.status):
            errors['status'] = f"Status must be one of: {', '.join(OrderStatus.all())}"
        
        # Validate items
        if not self.items:
            errors['items'] = "Order must have at least one item"
        
        if errors:
            raise ValidationError(errors)
    
    def add_item(self, item: OrderItem) -> None:
        """
        Add an item to the order.
        
        Args:
            item: Order item to add
            
        Raises:
            BusinessRuleError: If order is in a final status
        """
        if OrderStatus.is_final(self.status):
            raise BusinessRuleError(f"Cannot add items to an order with status '{self.status}'")
        
        # Set order_id on the item
        item.order_id = self.id
        
        # Add item to the order
        self.items.append(item)
        
        # Recalculate total
        self.calculate_total()
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    def remove_item(self, item_id: int) -> None:
        """
        Remove an item from the order.
        
        Args:
            item_id: ID of the item to remove
            
        Raises:
            BusinessRuleError: If order is in a final status
            ValueError: If item not found
        """
        if OrderStatus.is_final(self.status):
            raise BusinessRuleError(f"Cannot remove items from an order with status '{self.status}'")
        
        # Find the item
        for i, item in enumerate(self.items):
            if item.id == item_id:
                # Remove the item
                self.items.pop(i)
                
                # Recalculate total
                self.calculate_total()
                
                # Update timestamp
                self.updated_at = datetime.utcnow()
                return
        
        raise ValueError(f"Item with ID {item_id} not found in order")
    
    def update_item_quantity(self, item_id: int, quantity: int) -> None:
        """
        Update the quantity of an item in the order.
        
        Args:
            item_id: ID of the item to update
            quantity: New quantity
            
        Raises:
            BusinessRuleError: If order is in a final status
            ValueError: If item not found or quantity is invalid
        """
        if OrderStatus.is_final(self.status):
            raise BusinessRuleError(f"Cannot update items in an order with status '{self.status}'")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        # Find the item
        for item in self.items:
            if item.id == item_id:
                # Update the quantity
                item.quantity = quantity
                
                # Recalculate total
                self.calculate_total()
                
                # Update timestamp
                self.updated_at = datetime.utcnow()
                return
        
        raise ValueError(f"Item with ID {item_id} not found in order")
    
    def calculate_total(self) -> Money:
        """
        Calculate the total amount of the order.
        
        Returns:
            Money: Total amount
        """
        total = Money(Decimal('0.00'))
        
        for item in self.items:
            total += item.subtotal
        
        self.total_amount = total
        return total
    
    def update_status(self, new_status: str) -> None:
        """
        Update the status of the order.
        
        Args:
            new_status: New status
            
        Raises:
            ValidationError: If status is invalid
            InvalidStatusTransitionError: If status transition is invalid
        """
        if not OrderStatus.is_valid(new_status):
            raise ValidationError({'status': f"Status must be one of: {', '.join(OrderStatus.all())}"})
        
        if not OrderStatus.can_transition(self.status, new_status):
            raise InvalidStatusTransitionError(
                entity_type="Order",
                current_status=self.status,
                new_status=new_status
            )
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """
        Cancel the order.
        
        Raises:
            BusinessRuleError: If order cannot be cancelled
        """
        if self.status == OrderStatus.CANCELLED:
            raise BusinessRuleError("Order is already cancelled")
        
        if self.status == OrderStatus.DELIVERED:
            raise BusinessRuleError("Cannot cancel a delivered order")
        
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def set_tracking_number(self, tracking_number: str) -> None:
        """
        Set the tracking number for the order.
        
        Args:
            tracking_number: Tracking number
        """
        self.tracking_number = tracking_number
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_items: bool = True) -> Dict[str, Any]:
        """
        Convert order to dictionary.
        
        Args:
            include_items: Whether to include order items
            
        Returns:
            Dict[str, Any]: Order as dictionary
        """
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'total_amount': float(self.total_amount.amount) if self.total_amount else None,
            'shipping_address': self.shipping_address.to_dict() if self.shipping_address else None,
            'tracking_number': self.tracking_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_items:
            result['items'] = [item.to_dict() for item in self.items]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """
        Create an Order from a dictionary.
        
        Args:
            data: Dictionary with order attributes
            
        Returns:
            Order: Order instance
        """
        # Convert string timestamps to datetime objects if present
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        # Convert total_amount to Money object
        total_amount = data.get('total_amount')
        if total_amount is not None and not isinstance(total_amount, Money):
            total_amount = Money(Decimal(str(total_amount)))
        
        # Convert shipping_address to Address object
        shipping_address = data.get('shipping_address')
        if shipping_address is not None and not isinstance(shipping_address, Address):
            shipping_address = Address.from_dict(shipping_address)
        
        # Convert items to OrderItem objects
        items = []
        for item_data in data.get('items', []):
            items.append(OrderItem.from_dict(item_data))
        
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id', 0),
            status=data.get('status', OrderStatus.PENDING),
            total_amount=total_amount,
            shipping_address=shipping_address,
            tracking_number=data.get('tracking_number'),
            notes=data.get('notes', ''),
            items=items,
            created_at=created_at,
            updated_at=updated_at
        )