"""
Order service.
"""
from sqlalchemy import desc
from app import db
from app.models import Order, OrderItem, Product, User, OrderStatus
from app.core.exceptions import NotFoundError, BusinessLogicError

class OrderService:
    """Service for order operations."""
    
    def get_orders_query(self, user_id=None, status=None):
        """
        Get orders query with filters.
        
        Args:
            user_id (str): Filter by Keycloak user ID
            status (str): Filter by order status
            
        Returns:
            Query: SQLAlchemy query object
        """
        # Start with base query
        query = Order.query
        
        # Filter by user if specified
        if user_id:
            user = User.query.filter_by(keycloak_id=user_id).first()
            if user:
                query = query.filter_by(user_id=user.id)
        
        # Filter by status if specified
        if status and status in OrderStatus.all():
            query = query.filter_by(status=status)
        
        # Order by created_at desc
        query = query.order_by(desc(Order.created_at))
        
        return query
    
    def get_order_by_id(self, order_id, user_id=None):
        """
        Get order by ID.
        
        Args:
            order_id (int): Order ID
            user_id (str): Keycloak user ID for authorization check
            
        Returns:
            Order: Order object
            
        Raises:
            NotFoundError: If order not found or user not authorized
        """
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundError(f"Order with ID {order_id} not found")
        
        # Check if user is authorized to view this order
        if user_id:
            user = User.query.filter_by(keycloak_id=user_id).first()
            if not user or order.user_id != user.id:
                raise NotFoundError(f"Order with ID {order_id} not found")
        
        return order
    
    def create_order(self, user_keycloak_id, order_data):
        """
        Create a new order.
        
        Args:
            user_keycloak_id (str): Keycloak user ID
            order_data (dict): Order data
            
        Returns:
            Order: Created order
            
        Raises:
            NotFoundError: If user not found
            BusinessLogicError: If business logic validation fails
        """
        # Get user
        user = User.query.filter_by(keycloak_id=user_keycloak_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        # Validate items and calculate total
        if 'items' not in order_data or not order_data['items']:
            raise BusinessLogicError("Order must contain at least one item")
        
        total_amount = 0
        order_items = []
        
        for item_data in order_data['items']:
            if 'product_id' not in item_data or 'quantity' not in item_data:
                raise BusinessLogicError("Product ID and quantity are required for each item")
            
            product = Product.query.get(item_data['product_id'])
            if not product or not product.is_active:
                raise BusinessLogicError(f"Product with ID {item_data['product_id']} not found")
            
            if product.stock < item_data['quantity']:
                raise BusinessLogicError(f"Not enough stock for product {product.name}")
            
            # Calculate item price
            item_price = float(product.price) * item_data['quantity']
            total_amount += item_price
            
            # Create order item
            order_items.append({
                'product_id': product.id,
                'quantity': item_data['quantity'],
                'price': product.price
            })
            
            # Update product stock
            product.stock -= item_data['quantity']
        
        # Create order
        order = Order(
            user_id=user.id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            shipping_address=order_data.get('shipping_address', ''),
            notes=order_data.get('notes', '')
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return order
    
    def update_order_status(self, order_id, status):
        """
        Update order status.
        
        Args:
            order_id (int): Order ID
            status (str): New status
            
        Returns:
            Order: Updated order
            
        Raises:
            NotFoundError: If order not found
            BusinessLogicError: If status transition not allowed
        """
        order = self.get_order_by_id(order_id)
        
        # Validate status
        if status not in OrderStatus.all():
            valid_statuses = ", ".join(OrderStatus.all())
            raise BusinessLogicError(f"Status must be one of: {valid_statuses}")
        
        # Check if status transition is allowed
        if order.status == OrderStatus.CANCELLED and status != OrderStatus.CANCELLED:
            raise BusinessLogicError("Cannot change status of a cancelled order")
        
        if order.status == OrderStatus.DELIVERED and status != OrderStatus.DELIVERED:
            raise BusinessLogicError("Cannot change status of a delivered order")
        
        # If cancelling an order, restore product stock
        if status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
            self._restore_product_stock(order)
        
        order.status = status
        db.session.commit()
        
        return order
    
    def cancel_order(self, order_id, user_id=None):
        """
        Cancel an order.
        
        Args:
            order_id (int): Order ID
            user_id (str): Keycloak user ID for authorization check
            
        Returns:
            Order: Updated order
            
        Raises:
            NotFoundError: If order not found or user not authorized
            BusinessLogicError: If order cannot be cancelled
        """
        order = self.get_order_by_id(order_id, user_id)
        
        # Check if order can be cancelled
        if order.status == OrderStatus.CANCELLED:
            raise BusinessLogicError("Order is already cancelled")
        
        if order.status in [OrderStatus.DELIVERED, OrderStatus.SHIPPED]:
            raise BusinessLogicError(f"Cannot cancel order with status '{order.status}'")
        
        # Restore product stock
        self._restore_product_stock(order)
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        db.session.commit()
        
        return order
    
    def _restore_product_stock(self, order):
        """
        Restore product stock for an order.
        
        Args:
            order (Order): Order object
        """
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity