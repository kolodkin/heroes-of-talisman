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

# install client dependencies
npm install

# Start the services
docker compose up -d

# Run database migrations
# python -m server.database
# Wait for postgres to be up
echo "Waiting for postgres to be ready..."
until docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; do
  sleep 1
done
echo "Postgres is ready."

alembic upgrade head
