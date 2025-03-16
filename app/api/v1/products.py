"""
Product API endpoints.
"""
from flask import request, jsonify, current_app
from app.api import api_bp
from app.services.product import ProductService
from app.core.decorators import token_required
from app.core.exceptions import ValidationError, NotFoundError
from app.core.schemas import ProductSchema
from app.core.pagination import paginate

@api_bp.route('/v1/products', methods=['GET'])
def get_products():
    """
    Get products endpoint.
    
    Returns:
        JSON: Paginated list of products
    """
    try:
        product_service = ProductService()
        
        # Get query parameters
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Get products query
        query = product_service.get_products_query(
            search=search,
            category=category,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Paginate results
        return paginate(query, ProductSchema())
    except Exception as e:
        current_app.logger.error(f"Error getting products: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/products/<int:id>', methods=['GET'])
def get_product(id):
    """
    Get product by ID endpoint.
    
    Args:
        id (int): Product ID
        
    Returns:
        JSON: Product details
    """
    try:
        product_service = ProductService()
        product = product_service.get_product_by_id(id)
        
        schema = ProductSchema()
        return jsonify(schema.dump(product)), 200
    except NotFoundError:
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting product {id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/products', methods=['POST'])
@token_required(roles=['admin'])
def create_product(current_user):
    """
    Create product endpoint.
    
    Args:
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Created product details
    """
    try:
        # Validate request data
        schema = ProductSchema()
        data = schema.load(request.get_json())
        
        # Create product
        product_service = ProductService()
        product = product_service.create_product(data)
        
        return jsonify(schema.dump(product)), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating product: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/products/<int:id>', methods=['PUT'])
@token_required(roles=['admin'])
def update_product(id, current_user):
    """
    Update product endpoint.
    
    Args:
        id (int): Product ID
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Updated product details
    """
    try:
        # Validate request data
        schema = ProductSchema(partial=True)
        data = schema.load(request.get_json())
        
        # Update product
        product_service = ProductService()
        product = product_service.update_product(id, data)
        
        return jsonify(schema.dump(product)), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors}), 400
    except NotFoundError:
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating product {id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/v1/products/<int:id>', methods=['DELETE'])
@token_required(roles=['admin'])
def delete_product(id, current_user):
    """
    Delete product endpoint.
    
    Args:
        id (int): Product ID
        current_user (dict): Current authenticated user
        
    Returns:
        JSON: Success message
    """
    try:
        product_service = ProductService()
        product_service.delete_product(id)
        
        return jsonify({'message': 'Product deleted successfully'}), 200
    except NotFoundError:
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting product {id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500