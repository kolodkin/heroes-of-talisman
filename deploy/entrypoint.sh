#!/bin/bash
set -e

# Entrypoint script for production deployment
# Installs dependencies and starts the FastAPI server

# Install curl for healthcheck
apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r /app/deploy/requirements.txt

# Install the application wheel package
echo "Installing application package..."
pip install /app/deploy/*.whl

# Start the FastAPI server using uvicorn
echo "Starting server..."
uvicorn server.main:app --host "${UVICORN_HOST:-0.0.0.0}" --port "${UVICORN_PORT:-8000}"
