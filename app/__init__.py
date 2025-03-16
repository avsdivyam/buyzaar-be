"""
Application initialization module.

This module initializes the Flask application and its extensions.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name="default"):
    """
    Create and configure a Flask application instance.
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register error handlers
    from app.interfaces.api.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Register API blueprints
    from app.interfaces.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app