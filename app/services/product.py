"""
Product service.
"""
from sqlalchemy import or_, and_
from app import db
from app.models import Product
from app.core.exceptions import NotFoundError, ValidationError
from app.services.storage import StorageService

class ProductService:
    """Service for product operations."""
    
    def get_products_query(self, search='', category='', min_price=None, max_price=None, 
                          sort_by='created_at', sort_order='desc'):
        """
        Get products query with filters.
        
        Args:
            search (str): Search term for name and description
            category (str): Category filter
            min_price (float): Minimum price filter
            max_price (float): Maximum price filter
            sort_by (str): Field to sort by
            sort_order (str): Sort order ('asc' or 'desc')
            
        Returns:
            Query: SQLAlchemy query object
        """
        # Start with base query for active products
        query = Product.query.filter_by(is_active=True)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Apply price filters
        if min_price is not None and max_price is not None:
            query = query.filter(and_(Product.price >= min_price, Product.price <= max_price))
        elif min_price is not None:
            query = query.filter(Product.price >= min_price)
        elif max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        # Apply sorting
        if sort_by not in ['name', 'price', 'created_at']:
            sort_by = 'created_at'
        
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        sort_column = getattr(Product, sort_by)
        if sort_order == 'desc':
            sort_column = sort_column.desc()
        
        query = query.order_by(sort_column)
        
        return query
    
    def get_product_by_id(self, product_id):
        """
        Get product by ID.
        
        Args:
            product_id (int): Product ID
            
        Returns:
            Product: Product object
            
        Raises:
            NotFoundError: If product not found
        """
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            raise NotFoundError(f"Product with ID {product_id} not found")
        return product
    
    def create_product(self, product_data):
        """
        Create a new product.
        
        Args:
            product_data (dict): Product data
            
        Returns:
            Product: Created product
            
        Raises:
            ValidationError: If validation fails
        """
        # Handle image upload if present
        if 'image_file' in product_data:
            storage_service = StorageService()
            image_url = storage_service.upload_file(
                product_data['image_file'],
                folder='products'
            )
            product_data['image_url'] = image_url
            del product_data['image_file']
        
        # Create product
        product = Product(**product_data)
        db.session.add(product)
        db.session.commit()
        
        return product
    
    def update_product(self, product_id, product_data):
        """
        Update a product.
        
        Args:
            product_id (int): Product ID
            product_data (dict): Product data
            
        Returns:
            Product: Updated product
            
        Raises:
            NotFoundError: If product not found
            ValidationError: If validation fails
        """
        product = self.get_product_by_id(product_id)
        
        # Handle image upload if present
        if 'image_file' in product_data:
            storage_service = StorageService()
            
            # Delete old image if exists
            if product.image_url:
                storage_service.delete_file(product.image_url)
            
            # Upload new image
            image_url = storage_service.upload_file(
                product_data['image_file'],
                folder='products'
            )
            product_data['image_url'] = image_url
            del product_data['image_file']
        
        # Update product attributes
        for key, value in product_data.items():
            setattr(product, key, value)
        
        db.session.commit()
        
        return product
    
    def delete_product(self, product_id):
        """
        Delete a product (soft delete).
        
        Args:
            product_id (int): Product ID
            
        Raises:
            NotFoundError: If product not found
        """
        product = self.get_product_by_id(product_id)
        
        # Soft delete
        product.is_active = False
        db.session.commit()
        
        return True