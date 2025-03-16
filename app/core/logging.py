"""
Logging configuration module.

This module provides utilities for configuring application logging.
"""
import logging
import sys
from flask import Flask, request

class RequestFormatter(logging.Formatter):
    """
    Custom formatter that includes request information in log records.
    """
    
    def format(self, record):
        """Format log record with request information."""
        record.url = request.url if request else "N/A"
        record.method = request.method if request else "N/A"
        record.remote_addr = request.remote_addr if request else "N/A"
        return super().format(record)


def configure_logging(app: Flask, log_level: str = "INFO"):
    """
    Configure application logging.
    
    Args:
        app: Flask application
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s - "%(method)s %(url)s" - '
        '%(levelname)s in %(module)s: %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Configure Flask logger
    app.logger.setLevel(numeric_level)
    
    # Log application startup
    app.logger.info(f"Application started with log level: {log_level}")
    
    return root_logger