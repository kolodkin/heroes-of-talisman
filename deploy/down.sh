#!/bin/bash
set -e

# Script to stop Heroes of Talisman deployment services
# Usage: ./down.sh

# Change to deploy directory
SCRIPT_DIR=$(dirname $(readlink -f $0))

pushd $SCRIPT_DIR > /dev/null

echo "Stopping deployment services..."
docker compose -p heroes-of-talisman down

echo "All services stopped successfully!"

popd > /dev/null
