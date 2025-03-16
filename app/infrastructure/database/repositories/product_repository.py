"""
Product repository implementation.

This module implements the product repository using SQLAlchemy ORM.
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy import or_, and_

from app import db
from app.domain.models.product import Product
from app.domain.value_objects.money import Money
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models.product import ProductModel


class ProductRepository:
    """Repository for Product domain model using SQLAlchemy ORM."""
    
    def get_by_id(self, product_id: int) -> Product:
        """
        Get a product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product: Product domain model
            
        Raises:
            NotFoundError: If product not found
        """
        product_model = ProductModel.query.get(product_id)
        if not product_model:
            raise NotFoundError(entity_type="Product", entity_id=product_id)
        
        return self._to_domain(product_model)
    
    def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get a product by SKU.
        
        Args:
            sku: Product SKU
            
        Returns:
            Optional[Product]: Product domain model or None if not found
        """
        product_model = ProductModel.query.filter_by(sku=sku).first()
        if not product_model:
            return None
        
        return self._to_domain(product_model)
    
    def get_all(self, page: int = 1, per_page: int = 10, search: str = "", 
               min_price: Optional[float] = None, max_price: Optional[float] = None,
               sort_by: str = "created_at", sort_order: str = "desc") -> List[Product]:
        """
        Get all products with optional filters and sorting.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            search: Search term for name and description
            min_price: Minimum price filter
            max_price: Maximum price filter
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            List[Product]: List of product domain models
        """
        query = ProductModel.query.filter_by(is_active=True)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    ProductModel.name.ilike(search_term),
                    ProductModel.description.ilike(search_term)
                )
            )
        
        # Apply price filters
        if min_price is not None and max_price is not None:
            query = query.filter(and_(ProductModel.price >= min_price, ProductModel.price <= max_price))
        elif min_price is not None:
            query = query.filter(ProductModel.price >= min_price)
        elif max_price is not None:
            query = query.filter(ProductModel.price <= max_price)
        
        # Apply sorting
        if sort_by not in ['name', 'price', 'created_at']:
            sort_by = 'created_at'
        
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        sort_column = getattr(ProductModel, sort_by)
        if sort_order == 'desc':
            sort_column = sort_column.desc()
        
        query = query.order_by(sort_column)
        
        # Apply pagination
        products = query.paginate(page=page, per_page=per_page)
        
        return [self._to_domain(product) for product in products.items]
    
    def create(self, product: Product) -> Product:
        """
        Create a new product.
        
        Args:
            product: Product domain model
            
        Returns:
            Product: Created product with ID
        """
        product_model = ProductModel(
            name=product.name,
            description=product.description,
            price=product.price.amount,
            image_url=product.image_url,
            stock=product.stock,
            sku=product.sku,
            is_active=product.is_active
        )
        
        db.session.add(product_model)
        db.session.commit()
        
        # Update domain model with generated ID
        product.id = product_model.id
        
        return product
    
    def update(self, product: Product) -> Product:
        """
        Update an existing product.
        
        Args:
            product: Product domain model
            
        Returns:
            Product: Updated product
            
        Raises:
            NotFoundError: If product not found
        """
        product_model = ProductModel.query.get(product.id)
        if not product_model:
            raise NotFoundError(entity_type="Product", entity_id=product.id)
        
        # Update model attributes
        product_model.name = product.name
        product_model.description = product.description
        product_model.price = product.price.amount
        product_model.image_url = product.image_url
        product_model.stock = product.stock
        product_model.sku = product.sku
        product_model.is_active = product.is_active
        
        db.session.commit()
        
        return product
    
    def delete(self, product_id: int) -> None:
        """
        Delete a product.
        
        Args:
            product_id: Product ID
            
        Raises:
            NotFoundError: If product not found
        """
        product_model = ProductModel.query.get(product_id)
        if not product_model:
            raise NotFoundError(entity_type="Product", entity_id=product_id)
        
        db.session.delete(product_model)
        db.session.commit()
    
    def update_stock(self, product_id: int, quantity: int) -> Product:
        """
        Update product stock.
        
        Args:
            product_id: Product ID
            quantity: Quantity to add (positive) or remove (negative)
            
        Returns:
            Product: Updated product
            
        Raises:
            NotFoundError: If product not found
        """
        product_model = ProductModel.query.get(product_id)
        if not product_model:
            raise NotFoundError(entity_type="Product", entity_id=product_id)
        
        # Update stock
        product_model.stock += quantity
        
        # Ensure stock is not negative
        if product_model.stock < 0:
            product_model.stock = 0
        
        db.session.commit()
        
        return self._to_domain(product_model)
    
    def _to_domain(self, product_model: ProductModel) -> Product:
        """
        Convert ORM model to domain model.
        
        Args:
            product_model: SQLAlchemy product model
            
        Returns:
            Product: Product domain model
        """
        return Product(
            id=product_model.id,
            name=product_model.name,
            description=product_model.description,
            price=Money(Decimal(str(product_model.price))),
            image_url=product_model.image_url,
            stock=product_model.stock,
            sku=product_model.sku,
            is_active=product_model.is_active,
            created_at=product_model.created_at,
            updated_at=product_model.updated_at
        )