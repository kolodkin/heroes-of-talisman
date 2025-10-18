#!/bin/bash
set -e
COMPOSE_BAKE=true # bake the docker-compose.yaml file into a single file

# Production deployment script for Heroes of Talisman
# Usage:
#   ./deploy.sh           - Start services without rebuilding frontend
#   ./deploy.sh --build   - Build frontend and start services
#   ./deploy.sh --nowait  - Skip health check wait
#   ./deploy.sh --build --nowait - Build and deploy without waiting

# Change to deploy directory
SCRIPT_DIR=$(dirname $(readlink -f $0))

pushd $SCRIPT_DIR > /dev/null

# Parse flags
BUILD=false
NOWAIT=false

for arg in "$@"; do
  case $arg in
    --build)
      BUILD=true
      ;;
    --nowait)
      NOWAIT=true
      ;;
  esac
done

# Build if requested
if [[ "$BUILD" == "true" ]]; then
  echo "Building frontend before deployment..."
  ./build.sh
fi

# Start docker-compose services from deploy directory
echo "Starting deployment services..."
docker compose -p heroes-of-talisman up -d --build

# Wait for health check unless --nowait is specified
if [[ "$NOWAIT" == "false" ]]; then
  echo ""
  echo "Waiting for application container to be healthy..."

  # Wait for the app container to be healthy using docker's health check
  CONTAINER_NAME="heroes-of-talisman-app-1"
  TIMEOUT=60
  ELAPSED=0

  while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null || echo "not_found")

    if [ "$HEALTH_STATUS" = "healthy" ]; then
      echo "Application is healthy!"
      break
    fi

    sleep 2
    ELAPSED=$((ELAPSED + 2))
  done

  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "Warning: Application did not become healthy within ${TIMEOUT}s"
    echo "Check logs: docker compose -p heroes-of-talisman logs -f app"
  fi
fi

echo ""
echo "Deployment complete!"
echo
echo "To view logs: docker compose -p heroes-of-talisman logs -f"
echo "To stop: docker compose -p heroes-of-talisman down"

popd > /dev/null