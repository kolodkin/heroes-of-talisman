#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=$SCRIPT_DIR/..

cd $ROOT_DIR

# check for docker command
docker_installed=$(command -v docker >/dev/null 2>&1 && echo "true" || echo "false")

# Parse --no-docker flag
for arg in "$@"; do
  if [ "$arg" = "--no-docker" ]; then
    docker_installed=false
  fi
done


if [ "$docker_installed" = "true" ]; then
  echo "Starting services with docker"
  docker compose up -d
else
  echo "docker not installed"

  # Check if pg_isready is available
  if ! command -v pg_isready >/dev/null 2>&1; then
    echo "Error: pg_isready is not installed or not in PATH."
    echo "Please install PostgreSQL client utilities (e.g., postgresql-client) before running this script."
    exit 1
  fi
fi

# Install dependencies
uv sync

# Create environment variables
./scripts/create_env.sh

# Install python pre-commit hooks
uv run pre-commit install
uv run pre-commit run --files "$0" # installs pre-commit hooks

# install client dependencies
npm install
npx playwright install --with-deps chromium

# Install npm git hooks for frontend
npx simple-git-hooks

# Run database migrations
# Wait for postgres to be up
echo "Waiting for postgres to be ready..."

# Use a for loop to wait up to 10 seconds for postgres to be ready, exit 1 on failure
if [ "$docker_installed" = "true" ]; then
  cmd="docker compose exec -T postgres pg_isready -U \"${POSTGRES_USER:-postgres}\" > /dev/null 2>&1"
else
  cmd="pg_isready -h \"${POSTGRES_HOST:-localhost}\" -p \"${POSTGRES_PORT:-5432}\" -U \"${POSTGRES_USER:-postgres}\" > /dev/null 2>&1"
fi

for i in {1..10}; do
  if eval "$cmd"; then
    break
  fi
  sleep 1
  if [ "$i" -eq 10 ]; then
    echo "Postgres did not become ready in time."
    exit 1
  fi
done
echo "Postgres is ready."

uv run alembic upgrade head

# AI instructions conversion
uv run scripts/ai.py -v
