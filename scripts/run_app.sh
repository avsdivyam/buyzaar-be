#!/bin/bash

# Set environment variables if not already set
export FLASK_APP=${FLASK_APP:-run.py}
export FLASK_CONFIG=${FLASK_CONFIG:-development}
export FLASK_DEBUG=${FLASK_DEBUG:-1}

# Check if database connection is working
echo "Checking database connection..."
python -m scripts.check_db

if [ $? -ne 0 ]; then
    echo "Database connection check failed. Please check your database configuration."
    exit 1
fi

# Check if Keycloak connection is working
echo "Checking Keycloak connection..."
python -m scripts.check_keycloak

if [ $? -ne 0 ]; then
    echo "Keycloak connection check failed. The application will continue, but authentication may not work properly."
    # Don't exit, just warn
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start the application
echo "Starting the application..."
if [ "$FLASK_CONFIG" = "production" ]; then
    echo "Running in production mode with gunicorn..."
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app
else
    echo "Running in development mode with Flask development server..."
    flask run --host=0.0.0.0

# # Set environment variables if not already set
# export FLASK_APP=${FLASK_APP:-run.py}
# export FLASK_CONFIG=${FLASK_CONFIG:-development}
# export FLASK_DEBUG=${FLASK_DEBUG:-1}

# # Check if database connection is working
# echo "Checking database connection..."
# python -m scripts.check_db

# if [ $? -ne 0 ]; then
#     echo "Database connection check failed. Please check your database configuration."
#     exit 1
# fi

# # Run database migrations
# echo "Running database migrations..."
# flask db upgrade

# # Start the application
# echo "Starting the application..."
# if [ "$FLASK_CONFIG" = "production" ]; then
#     echo "Running in production mode with gunicorn..."
#     gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app
# else
#     echo "Running in development mode with Flask development server..."
#     flask run --host=0.0.0.0
# fi