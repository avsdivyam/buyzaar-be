import os
import uuid
from datetime import datetime
from functools import wraps
from flask import request, jsonify, current_app

def generate_unique_filename(original_filename):
    """
    Generate a unique filename by adding a UUID and timestamp
    
    Args:
        original_filename (str): Original filename
    
    Returns:
        str: Unique filename
    """
    filename, extension = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    return f"{filename}_{timestamp}_{unique_id}{extension}"

def get_pagination_params():
    """
    Get pagination parameters from request
    
    Returns:
        tuple: (page, per_page)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to a reasonable value
    max_per_page = current_app.config.get('MAX_PER_PAGE', 100)
    per_page = min(per_page, max_per_page)
    
    return page, per_page

def format_response(data, status_code=200):
    """
    Format a JSON response
    
    Args:
        data (dict): Response data
        status_code (int, optional): HTTP status code
    
    Returns:
        tuple: (response, status_code)
    """
    return jsonify(data), status_code

def handle_error(error_message, status_code=400):
    """
    Handle an error response
    
    Args:
        error_message (str): Error message
        status_code (int, optional): HTTP status code
    
    Returns:
        tuple: (response, status_code)
    """
    return jsonify({'error': error_message}), status_code