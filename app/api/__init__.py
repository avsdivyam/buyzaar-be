"""
API package for all API routes.
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from app.api.v1 import auth, products, orders, users