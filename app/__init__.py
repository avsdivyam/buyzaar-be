"""
Application initialization module.

This module initializes the Flask application and its extensions.
"""
import os
import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

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

    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register error handlers
    from app.interfaces.api.middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    # Register API blueprints
    from app.interfaces.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Initialize database
    from app.utils.db_utils import initialize_db
    with app.app_context():
        initialize_db(app, db)

    # Register health check endpoint with database status
    @app.route('/health')
    def health_check():
        from app.utils.db_utils import check_db_connection

        health_status = {
            'status': 'healthy',
            'database': 'connected'
        }

        # Check database connection
        try:
            if not check_db_connection(db):
                health_status['status'] = 'degraded'
                health_status['database'] = 'disconnected'
        except Exception as e:
            app.logger.error(f"Health check database error: {str(e)}")
            health_status['status'] = 'degraded'
            health_status['database'] = 'error'

        return jsonify(health_status)

    # Log application startup
    app.logger.info(f"Application started in {config_name} mode")
    app.logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0].split('://')[0] if '://' in app.config['SQLALCHEMY_DATABASE_URI'] else 'unknown'}")

    return app