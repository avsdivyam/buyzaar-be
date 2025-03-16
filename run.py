#!/usr/bin/env python3
"""
Application entry point.
"""
import os
from app import create_app

# Get configuration from environment
config_name = os.environ.get('FLASK_CONFIG', 'default')
app = create_app(config_name)

if __name__ == "__main__":
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    app.run(host=host, port=port, debug=debug)