"""
Order API endpoints.
"""
from flask import request, jsonify, current_app
from app.api import api_bp
from app.services.order import OrderService
from app.core.decorators import token_required
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.schemas import OrderSchema, OrderCreateSchema
from app.core.pagination import paginate

@api_bp.route('/v1/orders', methods=['GET'])
@token_required()
def get_orders(current_user):
    """
    Get orders endpoint.
    
    Args:
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Paginated list of orders
    """
    try:
        order_service = OrderService()
        
        # Get query parameters
        status = request.args.get('status', '')
        
        # Get orders query (filtered by user if not admin)
        is_admin = 'admin' in current_user.get('roles', [])
        query = order_service.get_orders_query(
            user_id=None if is_admin else current_user['sub'],
            status=status
        )
        
        # Paginate results
        return paginate(query, OrderSchema())
    except Exception as e:
        current_app.logger.error(f"Error getting orders: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/orders/<int:id>', methods=['GET'])
@token_required()
def get_order(id, current_user):
    """
    Get order by ID endpoint.
    
    Args:
        id (int): Order ID
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Order details
    """
    try:
        order_service = OrderService()
        
        # Check if user is authorized to view this order
        is_admin = 'admin' in current_user.get('roles', [])
        order = order_service.get_order_by_id(
            id, 
            user_id=None if is_admin else current_user['sub']
        )
        
        schema = OrderSchema()
        return jsonify(schema.dump(order)), 200
    except NotFoundError:
        return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting order {id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/orders', methods=['POST'])
@token_required()
def create_order(current_user):
    """
    Create order endpoint.
    
    Args:
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Created order details
    """
    try:
        # Validate request data
        schema = OrderCreateSchema()
        data = schema.load(request.get_json())
        
        # Create order
        order_service = OrderService()
        order = order_service.create_order(current_user['sub'], data)
        
        return jsonify(OrderSchema().dump(order)), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating order: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/orders/<int:id>/status', methods=['PUT'])
@token_required(roles=['admin'])
def update_order_status(id, current_user):
    """
    Update order status endpoint.
    
    Args:
        id (int): Order ID
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Updated order details
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data or 'status' not in data:
            raise ValidationError({'status': ['Status is required']})
        
        # Update order status
        order_service = OrderService()
        order = order_service.update_order_status(id, data['status'])
        
        schema = OrderSchema()
        return jsonify(schema.dump(order)), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except NotFoundError:
        return jsonify({'error': 'Order not found'}), 404
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating order status {id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/orders/<int:id>/cancel', methods=['POST'])
@token_required()
def cancel_order(id, current_user):
    """
    Cancel order endpoint.
    
    Args:
        id (int): Order ID
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Updated order details
    """
    try:
        order_service = OrderService()
        
        # Check if user is authorized to cancel this order
        is_admin = 'admin' in current_user.get('roles', [])
        order = order_service.cancel_order(
            id, 
            user_id=None if is_admin else current_user['sub']
        )
        
        schema = OrderSchema()
        return jsonify(schema.dump(order)), 200
    except NotFoundError:
        return jsonify({'error': 'Order not found'}), 404
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error cancelling order {id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500