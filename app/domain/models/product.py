"""
Product domain model.

This module defines the Product domain model and related value objects.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from app.domain.exceptions import ValidationError, InsufficientInventoryError
from app.domain.value_objects.money import Money


@dataclass
class Product:
    """Product domain model representing a product in the system."""
    
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    price: Money = None
    image_url: str = ""
    stock: int = 0
    sku: Optional[str] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Validate product attributes after initialization."""
        # Initialize price if provided as number
        if self.price is None:
            self.price = Money(Decimal('0.00'))
        elif isinstance(self.price, (int, float, str, Decimal)):
            self.price = Money(Decimal(str(self.price)))
        
        self.validate()
        
        # Set timestamps if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def validate(self) -> None:
        """
        Validate product attributes.
        
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Validate name
        if not self.name:
            errors['name'] = "Name is required"
        
        # Validate price
        if self.price is None or self.price.amount <= 0:
            errors['price'] = "Price must be greater than zero"
        
        # Validate stock
        if self.stock < 0:
            errors['stock'] = "Stock cannot be negative"
        
        if errors:
            raise ValidationError(errors)
    
    def update(self, data: Dict[str, Any]) -> None:
        """
        Update product attributes.
        
        Args:
            data: Dictionary of attributes to update
            
        Raises:
            ValidationError: If validation fails
        """
        # Update attributes
        if 'name' in data:
            self.name = data['name']
        if 'description' in data:
            self.description = data['description']
        if 'price' in data:
            if isinstance(data['price'], Money):
                self.price = data['price']
            else:
                self.price = Money(Decimal(str(data['price'])))
        if 'image_url' in data:
            self.image_url = data['image_url']
        if 'stock' in data:
            self.stock = data['stock']
        if 'sku' in data:
            self.sku = data['sku']
        if 'is_active' in data:
            self.is_active = data['is_active']
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
        
        # Validate updated attributes
        self.validate()
    
    def deactivate(self) -> None:
        """Deactivate the product."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate the product."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_stock(self, quantity: int) -> None:
        """
        Update product stock.
        
        Args:
            quantity: Quantity to add (positive) or remove (negative)
            
        Raises:
            InsufficientInventoryError: If removing more than available
        """
        if quantity < 0 and abs(quantity) > self.stock:
            raise InsufficientInventoryError(
                product_id=self.id,
                product_name=self.name,
                requested=abs(quantity),
                available=self.stock
            )
        
        self.stock += quantity
        self.updated_at = datetime.utcnow()
    
    def reserve_stock(self, quantity: int) -> None:
        """
        Reserve product stock for an order.
        
        Args:
            quantity: Quantity to reserve
            
        Raises:
            InsufficientInventoryError: If not enough stock available
        """
        self.update_stock(-quantity)
    
    def release_stock(self, quantity: int) -> None:
        """
        Release previously reserved stock.
        
        Args:
            quantity: Quantity to release
        """
        self.update_stock(quantity)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert product to dictionary.
        
        Returns:
            Dict[str, Any]: Product as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price.amount) if self.price else None,
            'image_url': self.image_url,
            'stock': self.stock,
            'sku': self.sku,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """
        Create a Product from a dictionary.
        
        Args:
            data: Dictionary with product attributes
            
        Returns:
            Product: Product instance
        """
        # Convert string timestamps to datetime objects if present
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        # Convert price to Money object
        price = data.get('price')
        if price is not None and not isinstance(price, Money):
            price = Money(Decimal(str(price)))
        
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            price=price,
            image_url=data.get('image_url', ''),
            stock=data.get('stock', 0),
            sku=data.get('sku'),
            is_active=data.get('is_active', True),
            created_at=created_at,
            updated_at=updated_at
        )