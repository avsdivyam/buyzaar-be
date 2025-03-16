from flask import Blueprint, request, jsonify
from app import db
from app.models import Product
from app.utils.security import token_required

bp = Blueprint('products', __name__)

@bp.route('/', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    products = Product.query.paginate(page=page, per_page=per_page)
    
    result = {
        'items': [{
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'image_url': product.image_url,
            'stock': product.stock,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat()
        } for product in products.items],
        'total': products.total,
        'pages': products.pages,
        'page': page
    }
    
    return jsonify(result), 200

@bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    
    result = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url,
        'stock': product.stock,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat()
    }
    
    return jsonify(result), 200

@bp.route('/', methods=['POST'])
@token_required(roles=['admin'])
def create_product():
    data = request.get_json()
    
    required_fields = ['name', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        image_url=data.get('image_url', ''),
        stock=data.get('stock', 0)
    )
    
    db.session.add(product)
    db.session.commit()
    
    result = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url,
        'stock': product.stock,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat()
    }
    
    return jsonify(result), 201

@bp.route('/<int:id>', methods=['PUT'])
@token_required(roles=['admin'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'stock' in data:
        product.stock = data['stock']
    
    db.session.commit()
    
    result = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url,
        'stock': product.stock,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat()
    }
    
    return jsonify(result), 200

@bp.route('/<int:id>', methods=['DELETE'])
@token_required(roles=['admin'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'}), 200