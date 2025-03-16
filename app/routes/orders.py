from flask import Blueprint, request, jsonify
from app import db
from app.models import Order, OrderItem, Product, User
from app.utils.security import token_required

bp = Blueprint('orders', __name__)

@bp.route('/', methods=['GET'])
@token_required()
def get_orders(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Regular users can only see their own orders
    # Admins can see all orders
    if 'admin' in current_user.get('roles', []):
        orders = Order.query.paginate(page=page, per_page=per_page)
    else:
        user = User.query.filter_by(keycloak_id=current_user['sub']).first_or_404()
        orders = Order.query.filter_by(user_id=user.id).paginate(page=page, per_page=per_page)
    
    result = {
        'items': [{
            'id': order.id,
            'user_id': order.user_id,
            'status': order.status,
            'total_amount': order.total_amount,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'items': [{
                'id': item.id,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': item.price
            } for item in order.items]
        } for order in orders.items],
        'total': orders.total,
        'pages': orders.pages,
        'page': page
    }
    
    return jsonify(result), 200

@bp.route('/<int:id>', methods=['GET'])
@token_required()
def get_order(id, current_user):
    order = Order.query.get_or_404(id)
    
    # Check if the user is authorized to view this order
    if 'admin' not in current_user.get('roles', []):
        user = User.query.filter_by(keycloak_id=current_user['sub']).first_or_404()
        if order.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    result = {
        'id': order.id,
        'user_id': order.user_id,
        'status': order.status,
        'total_amount': order.total_amount,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
        'items': [{
            'id': item.id,
            'product_id': item.product_id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': item.price
        } for item in order.items]
    }
    
    return jsonify(result), 200

@bp.route('/', methods=['POST'])
@token_required()
def create_order(current_user):
    data = request.get_json()
    
    if not data or 'items' not in data or not data['items']:
        return jsonify({'error': 'Order items are required'}), 400
    
    # Get the user
    user = User.query.filter_by(keycloak_id=current_user['sub']).first_or_404()
    
    # Validate items and calculate total
    total_amount = 0
    order_items = []
    
    for item_data in data['items']:
        if 'product_id' not in item_data or 'quantity' not in item_data:
            return jsonify({'error': 'Product ID and quantity are required for each item'}), 400
        
        product = Product.query.get_or_404(item_data['product_id'])
        
        if product.stock < item_data['quantity']:
            return jsonify({'error': f'Not enough stock for product {product.name}'}), 400
        
        # Calculate item price
        item_price = product.price * item_data['quantity']
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
        status='pending',
        total_amount=total_amount
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
    
    result = {
        'id': order.id,
        'user_id': order.user_id,
        'status': order.status,
        'total_amount': order.total_amount,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
        'items': [{
            'id': item.id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': item.price
        } for item in order.items]
    }
    
    return jsonify(result), 201

@bp.route('/<int:id>/status', methods=['PUT'])
@token_required(roles=['admin'])
def update_order_status(id, current_user):
    order = Order.query.get_or_404(id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    valid_statuses = ['pending', 'completed', 'cancelled']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f'Status must be one of: {", ".join(valid_statuses)}'}), 400
    
    # If cancelling an order, restore product stock
    if data['status'] == 'cancelled' and order.status != 'cancelled':
        for item in order.items:
            product = Product.query.get(item.product_id)
            product.stock += item.quantity
    
    order.status = data['status']
    db.session.commit()
    
    result = {
        'id': order.id,
        'user_id': order.user_id,
        'status': order.status,
        'total_amount': order.total_amount,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat()
    }
    
    return jsonify(result), 200