"""
Error handlers for the application.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
from app.core.exceptions import (
    AppError, ValidationError, NotFoundError, 
    AuthenticationError, AuthorizationError, BusinessLogicError
)

def register_error_handlers(app):
    """
    Register error handlers for the application.
    
    Args:
        app: Flask application
    """
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            'error': 'Validation error',
            'details': e.errors
        }), 400
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        return jsonify({
            'error': str(e)
        }), 404
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(e):
        return jsonify({
            'error': str(e)
        }), 401
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(e):
        return jsonify({
            'error': str(e)
        }), 403
    
    @app.errorhandler(BusinessLogicError)
    def handle_business_logic_error(e):
        return jsonify({
            'error': str(e)
        }), 400
    
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({
            'error': str(e)
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            'error': e.description
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred'
        }), 500