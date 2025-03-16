"""
Product database model.

This module defines the SQLAlchemy ORM model for the Product entity.
"""
from datetime import datetime
from app import db


class ProductModel(db.Model):
    """SQLAlchemy model for the products table."""
    
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255))
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), unique=True, index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItemModel', backref='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.name}>'