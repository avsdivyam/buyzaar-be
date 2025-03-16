"""
API v1 package.
"""
from app.api import api_bp

# Import routes to register them with the blueprint
from app.api.v1 import auth, products, orders, users