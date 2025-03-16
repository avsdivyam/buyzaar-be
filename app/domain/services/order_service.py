"""
Order domain service.

This module defines the OrderService for order-related business logic.
"""
from typing import List, Dict, Any, Optional

from app.domain.models.order import Order, OrderItem, OrderStatus
from app.domain.models.product import Product
from app.domain.exceptions import BusinessRuleError, InsufficientInventoryError


class OrderService:
    """Domain service for order-related business logic."""
    
    @staticmethod
    def create_order_from_products(user_id: int, products: List[Dict[str, Any]], 
                                  shipping_address: Dict[str, Any], notes: str = "") -> Order:
        """
        Create an order from a list of products.
        
        Args:
            user_id: User ID
            products: List of product dictionaries with product_id and quantity
            shipping_address: Shipping address dictionary
            notes: Order notes
            
        Returns:
            Order: Created order
            
        Raises:
            BusinessRuleError: If products list is empty
            ValueError: If product data is invalid
        """
        if not products:
            raise BusinessRuleError("Order must contain at least one product")
        
        # Create order
        order = Order(
            user_id=user_id,
            shipping_address=shipping_address,
            notes=notes
        )
        
        # Add items to order
        for product_data in products:
            if 'product_id' not in product_data or 'quantity' not in product_data:
                raise ValueError("Product ID and quantity are required for each product")
            
            # This would normally fetch the product from a repository
            # Here we're just validating the input
            product_id = product_data['product_id']
            quantity = product_data['quantity']
            
            if not isinstance(product_id, int) or product_id <= 0:
                raise ValueError(f"Invalid product ID: {product_id}")
            
            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(f"Invalid quantity for product {product_id}: {quantity}")
        
        return order
    
    @staticmethod
    def add_product_to_order(order: Order, product: Product, quantity: int) -> OrderItem:
        """
        Add a product to an order.
        
        Args:
            order: Order to add product to
            product: Product to add
            quantity: Quantity to add
            
        Returns:
            OrderItem: Created order item
            
        Raises:
            BusinessRuleError: If order is in a final status
            InsufficientInventoryError: If product stock is insufficient
        """
        if OrderStatus.is_final(order.status):
            raise BusinessRuleError(f"Cannot add products to an order with status '{order.status}'")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        # Check product stock
        if product.stock < quantity:
            raise InsufficientInventoryError(
                product_id=product.id,
                product_name=product.name,
                requested=quantity,
                available=product.stock
            )
        
        # Create order item
        order_item = OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            price=product.price
        )
        
        # Add item to order
        order.add_item(order_item)
        
        # Reserve product stock
        product.reserve_stock(quantity)
        
        return order_item
    
    @staticmethod
    def cancel_order(order: Order, products: List[Product]) -> None:
        """
        Cancel an order and restore product stock.
        
        Args:
            order: Order to cancel
            products: List of products in the order
            
        Raises:
            BusinessRuleError: If order cannot be cancelled
        """
        # Cancel the order
        order.cancel()
        
        # Restore product stock
        for item in order.items:
            for product in products:
                if product.id == item.product_id:
                    product.release_stock(item.quantity)
                    break
    
    @staticmethod
    def can_update_order_status(order: Order, new_status: str) -> bool:
        """
        Check if an order status can be updated.
        
        Args:
            order: Order to check
            new_status: New status
            
        Returns:
            bool: True if status can be updated
        """
        return OrderStatus.can_transition(order.status, new_status)