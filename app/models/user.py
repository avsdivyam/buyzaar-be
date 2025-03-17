# """
# User model module.

# This module defines the User model for the application.
# """
# from datetime import datetime
# from app import db
# from app.utils.db_utils import with_db_retry

# class User(db.Model):
#     """User model for authentication and user management."""
    
#     __tablename__ = 'users'
    
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False, index=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(128), nullable=False)
#     first_name = db.Column(db.String(50), nullable=True)
#     last_name = db.Column(db.String(50), nullable=True)
#     is_active = db.Column(db.Boolean, default=True)
#     is_admin = db.Column(db.Boolean, default=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     def __repr__(self):
#         return f'<User {self.username}>'
    
#     @classmethod
#     @with_db_retry(max_retries=3)
#     def get_by_id(cls, user_id):
#         """Get user by ID with retry logic for database operations."""
#         return cls.query.get(user_id)
    
#     @classmethod
#     @with_db_retry(max_retries=3)
#     def get_by_email(cls, email):
#         """Get user by email with retry logic for database operations."""
#         return cls.query.filter_by(email=email).first()
    
#     @classmethod
#     @with_db_retry(max_retries=3)
#     def get_by_username(cls, username):
#         """Get user by username with retry logic for database operations."""
#         return cls.query.filter_by(username=username).first()
    
#     @with_db_retry(max_retries=3)
#     def save(self):
#         """Save user to database with retry logic."""
#         db.session.add(self)
#         db.session.commit()
#         return self
    
#     @with_db_retry(max_retries=3)
#     def delete(self):
#         """Delete user from database with retry logic."""
#         db.session.delete(self)
#         db.session.commit()
        
#     def to_dict(self):
#         """Convert user to dictionary for API responses."""
#         return {
#             'id': self.id,
#             'email': self.email,
#             'username': self.username,
#             'first_name': self.first_name,
#             'last_name': self.last_name,
#             'is_active': self.is_active,
#             'is_admin': self.is_admin,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None
#         }
"""
User model module.
"""
from datetime import datetime
from app import db

class User(db.Model):
    """User model representing application users."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    keycloak_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'keycloak_id': self.keycloak_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }