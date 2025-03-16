"""
Pagination utilities module.

This module provides utilities for paginating query results.
"""
from flask import request, current_app
from typing import Dict, Any, Tuple, List
from sqlalchemy.orm.query import Query


def get_pagination_params() -> Tuple[int, int]:
    """
    Get pagination parameters from request.
    
    Returns:
        Tuple[int, int]: (page, per_page)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 
                               current_app.config.get('DEFAULT_PAGE_SIZE', 10), 
                               type=int)
    
    # Ensure page is at least 1
    page = max(1, page)
    
    # Limit per_page to a reasonable value
    max_per_page = current_app.config.get('MAX_PAGE_SIZE', 100)
    per_page = min(max(1, per_page), max_per_page)
    
    return page, per_page


def paginate_query(query: Query, page: int, per_page: int) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Number of items per page
        
    Returns:
        Tuple[List[Any], Dict[str, Any]]: (items, pagination_info)
    """
    # Execute pagination
    paginated = query.paginate(page=page, per_page=per_page)
    
    # Extract items
    items = paginated.items
    
    # Build pagination info
    pagination = {
        'total': paginated.total,
        'pages': paginated.pages,
        'page': page,
        'per_page': per_page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }
    
    return items, pagination


def create_pagination_response(items: List[Any], pagination: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized pagination response.
    
    Args:
        items: List of items
        pagination: Pagination information
        
    Returns:
        Dict[str, Any]: Response dictionary
    """
    return {
        'items': items,
        'pagination': pagination
    }