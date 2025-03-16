"""
Order repository implementation.

This module implements the order repository using SQLAlchemy ORM.
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy import desc

from app import db
from app.domain.models.order import Order, OrderItem, OrderStatus
from app.domain.value_objects.money import Money
from app.domain.value_objects.address import Address
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models.order import OrderModel, OrderItemModel


class OrderRepository:
    """Repository for Order domain model using SQLAlchemy ORM."""
    
    def get_by_id(self, order_id: int) -> Order:
        """
        Get an order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order: Order domain model
            
        Raises:
            NotFoundError: If order not found
        """
        order_model = OrderModel.query.get(order_id)
        if not order_model:
            raise NotFoundError(entity_type="Order", entity_id=order_id)
        
        return self._to_domain(order_model)
    
    def get_by_user_id(self, user_id: int, page: int = 1, per_page: int = 10, 
                      status: Optional[str] = None) -> List[Order]:
        """
        Get orders by user ID.
        
        Args:
            user_id: User ID
            page: Page number (1-indexed)
            per_page: Number of items per page
            status: Filter by order status
            
        Returns:
            List[Order]: List of order domain models
        """
        query = OrderModel.query.filter_by(user_id=user_id)
        
        # Apply status filter
        if status and status in OrderStatus.all():
            query = query.filter_by(status=status)
        
        # Apply sorting
        query = query.order_by(desc(OrderModel.created_at))
        
        # Apply pagination
        orders = query.paginate(page=page, per_page=per_page)
        
        return [self._to_domain(order) for order in orders.items]
    
    def get_all(self, page: int = 1, per_page: int = 10, status: Optional[str] = None) -> List[Order]:
        """
        Get all orders with optional filters.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            status: Filter by order status
            
        Returns:
            List[Order]: List of order domain models
        """
        query = OrderModel.query
        
        # Apply status filter
        if status and status in OrderStatus.all():
            query = query.filter_by(status=status)
        
        # Apply sorting
        query = query.order_by(desc(OrderModel.created_at))
        
        # Apply pagination
        orders = query.paginate(page=page, per_page=per_page)
        
        return [self._to_domain(order) for order in orders.items]
    
    def create(self, order: Order) -> Order:
        """
        Create a new order.
        
        Args:
            order: Order domain model
            
        Returns:
            Order: Created order with ID
        """
        # Create order model
        order_model = OrderModel(
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount.amount,
            shipping_address=str(order.shipping_address) if order.shipping_address else None,
            tracking_number=order.tracking_number,
            notes=order.notes
        )
        
        db.session.add(order_model)
        db.session.flush()  # Get the order ID
        
        # Create order item models
        for item in order.items:
            item_model = OrderItemModel(
                order_id=order_model.id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                price=item.price.amount
            )
            db.session.add(item_model)
        
        db.session.commit()
        
        # Update domain model with generated ID
        order.id = order_model.id
        
        # Update order items with generated IDs
        for i, item_model in enumerate(order_model.items):
            order.items[i].id = item_model.id
            order.items[i].order_id = order_model.id
        
        return order
    
    def update(self, order: Order) -> Order:
        """
        Update an existing order.
        
        Args:
            order: Order domain model
            
        Returns:
            Order: Updated order
            
        Raises:
            NotFoundError: If order not found
        """
        order_model = OrderModel.query.get(order.id)
        if not order_model:
            raise NotFoundError(entity_type="Order", entity_id=order.id)
        
        # Update order model attributes
        order_model.status = order.status
        order_model.total_amount = order.total_amount.amount
        order_model.shipping_address = str(order.shipping_address) if order.shipping_address else None
        order_model.tracking_number = order.tracking_number
        order_model.notes = order.notes
        
        # Update existing items and add new items
        existing_item_ids = {item.id for item in order_model.items}
        updated_item_ids = set()
        
        for item in order.items:
            if item.id and item.id in existing_item_ids:
                # Update existing item
                item_model = OrderItemModel.query.get(item.id)
                item_model.product_id = item.product_id
                item_model.product_name = item.product_name
                item_model.quantity = item.quantity
                item_model.price = item.price.amount
                updated_item_ids.add(item.id)
            else:
                # Add new item
                item_model = OrderItemModel(
                    order_id=order.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price.amount
                )
                db.session.add(item_model)
        
        # Remove deleted items
        for item_id in existing_item_ids - updated_item_ids:
            item_model = OrderItemModel.query.get(item_id)
            db.session.delete(item_model)
        
        db.session.commit()
        
        return order
    
    def delete(self, order_id: int) -> None:
        """
        Delete an order.
        
        Args:
            order_id: Order ID
            
        Raises:
            NotFoundError: If order not found
        """
        order_model = OrderModel.query.get(order_id)
        if not order_model:
            raise NotFoundError(entity_type="Order", entity_id=order_id)
        
        db.session.delete(order_model)
        db.session.commit()
    
    def update_status(self, order_id: int, status: str) -> Order:
        """
        Update order status.
        
        Args:
            order_id: Order ID
            status: New status
            
        Returns:
            Order: Updated order
            
        Raises:
            NotFoundError: If order not found
        """
        order_model = OrderModel.query.get(order_id)
        if not order_model:
            raise NotFoundError(entity_type="Order", entity_id=order_id)
        
        order_model.status = status
        db.session.commit()
        
        return self._to_domain(order_model)
    
    def _to_domain(self, order_model: OrderModel) -> Order:
        """
        Convert ORM model to domain model.
        
        Args:
            order_model: SQLAlchemy order model
            
        Returns:
            Order: Order domain model
        """
        # Parse shipping address
        shipping_address = None
        if order_model.shipping_address:
            try:
                # This is a simplified approach - in a real app, you'd store address components separately
                address_parts = order_model.shipping_address.split(', ')
                if len(address_parts) >= 4:
                    street = address_parts[0]
                    city = address_parts[1]
                    state_zip = address_parts[2].split(' ')
                    state = state_zip[0]
                    postal_code = state_zip[1] if len(state_zip) > 1 else ''
                    country = address_parts[3]
                    
                    shipping_address = Address(
                        street=street,
                        city=city,
                        state=state,
                        postal_code=postal_code,
                        country=country
                    )
            except Exception:
                # If parsing fails, leave as None
                pass
        
        # Convert order items
        items = []
        for item_model in order_model.items:
            items.append(OrderItem(
                id=item_model.id,
                order_id=item_model.order_id,
                product_id=item_model.product_id,
                product_name=item_model.product_name,
                quantity=item_model.quantity,
                price=Money(Decimal(str(item_model.price)))
            ))
        
        return Order(
            id=order_model.id,
            user_id=order_model.user_id,
            status=order_model.status,
            total_amount=Money(Decimal(str(order_model.total_amount))),
            shipping_address=shipping_address,
            tracking_number=order_model.tracking_number,
            notes=order_model.notes,
            items=items,
            created_at=order_model.created_at,
            updated_at=order_model.updated_at
        )