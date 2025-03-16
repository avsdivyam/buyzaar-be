"""
API interfaces package.

This package contains API interfaces such as routes and controllers.
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from app.interfaces.api.v1 import auth