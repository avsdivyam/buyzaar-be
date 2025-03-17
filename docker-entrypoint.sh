#!/bin/sh

set -e

# Wait for the database to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h db -U dmtavs -d buyzaar; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Initialize the database if needed
echo "Initializing database..."
python -m scripts.init_db

# Set up Keycloak
echo "Setting up Keycloak..."
python -m scripts.setup_keycloak || echo "Keycloak setup failed, but continuing..."

# Start the application
echo "Starting the application..."
exec "$@"#!/bin/sh

set -e

# Wait for the database to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h db -U dmtavs -d buyzaar; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Initialize the database if needed
echo "Initializing database..."
python -m scripts.init_db

# Start the application
echo "Starting the application..."
exec "$@"