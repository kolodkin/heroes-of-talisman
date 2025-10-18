#!/bin/bash
set -e

# Entrypoint script for database migrations
# Installs dependencies and runs Alembic migrations

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r /app/deploy/requirements.txt

# Install the application wheel package
echo "Installing application package..."
pip install /app/deploy/*.whl

# Run Alembic migrations
echo "Running database migrations..."
cd /app/deploy
alembic upgrade head

echo "Migrations completed successfully!"
