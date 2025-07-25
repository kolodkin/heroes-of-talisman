#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=$SCRIPT_DIR/..

cd $ROOT_DIR

# Install dependencies
uv sync

# Create environment variables
./scripts/create_env.sh

# Activate virtual environment
source .venv/bin/activate

# Install pre-commit hooks
pre-commit install

# Run database migrations
# python -m server.database
# alembic upgrade head

# install client dependencies
npm install

# Start the services
docker compose up -d
