#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=$SCRIPT_DIR/..

cd $ROOT_DIR

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not installed, exiting..."
  exit 1
fi

docker compose up -d

# Install dependencies
uv sync

# Create environment variables
./scripts/create_env.sh

# Activate virtual environment
source .venv/bin/activate

# Install pre-commit hooks
uv run pre-commit install

# install client dependencies
npm install

# Start the services
echo "Starting services with docker..."

# Run database migrations
# Wait for postgres to be up
echo "Waiting for postgres to be ready..."
until docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; do
  sleep 1
done
echo "Postgres is ready."

uv run alembic upgrade head

# AI instructions conversion
uv run scripts/ai.py
