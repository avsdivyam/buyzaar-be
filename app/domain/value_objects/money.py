"""
Money value object.

This module defines the Money value object for representing monetary values.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Union, Dict, Any


@dataclass(frozen=True)
class Money:
    """
    Money value object representing a monetary value.
    
    This is an immutable value object that represents a monetary value
    with a fixed decimal precision.
    """
    
    amount: Decimal
    
    def __post_init__(self):
        """Ensure amount is a Decimal with proper precision."""
        # Use object.__setattr__ to modify frozen dataclass
        object.__setattr__(self, 'amount', Decimal(str(self.amount)).quantize(Decimal('0.01')))
    
    def __add__(self, other: 'Money') -> 'Money':
        """Add two Money objects."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        return Money(self.amount + other.amount)
    
    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract two Money objects."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        return Money(self.amount - other.amount)
    
    def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
        """Multiply Money by a scalar."""
        if not isinstance(multiplier, (int, float, Decimal)):
            raise TypeError("Can only multiply Money by a number")
        return Money(self.amount * Decimal(str(multiplier)))
    
    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
        """Divide Money by a scalar."""
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError("Can only divide Money by a number")
        if Decimal(str(divisor)) == 0:
            raise ZeroDivisionError("Cannot divide Money by zero")
        return Money(self.amount / Decimal(str(divisor)))
    
    def __lt__(self, other: 'Money') -> bool:
        """Compare if this Money is less than another."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        return self.amount < other.amount
    
    def __le__(self, other: 'Money') -> bool:
        """Compare if this Money is less than or equal to another."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        return self.amount <= other.amount
    
    def __gt__(self, other: 'Money') -> bool:
        """Compare if this Money is greater than another."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        return self.amount > other.amount
    
    def __ge__(self, other: 'Money') -> bool:
        """Compare if this Money is greater than or equal to another."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        return self.amount >= other.amount
    
    def __str__(self) -> str:
        """String representation of Money."""
        return f"{self.amount:.2f}"
    
    def __repr__(self) -> str:
        """Formal representation of Money."""
        return f"Money({self.amount})"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Money to dictionary.
        
        Returns:
            Dict[str, Any]: Money as dictionary
        """
        return {
            'amount': float(self.amount)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Money':
        """
        Create a Money from a dictionary.
        
        Args:
            data: Dictionary with money attributes
            
        Returns:
            Money: Money instance
        """
        return cls(Decimal(str(data['amount'])))