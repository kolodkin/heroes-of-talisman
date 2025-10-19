#!/bin/bash

# SSH Deploy Script
# Usage:
#   ./deploy/ssh-up.sh user@host              - Build and deploy
#   ./deploy/ssh-up.sh user@host --nobuild    - Deploy without rebuilding

set -e

# Check if SSH connection string is provided (and doesn't start with --)
if [ -z "$1" ] || [[ "$1" == --* ]]; then
    echo "Error: SSH connection string required"
    echo "Usage: $0 user@host [--nobuild]"
    exit 1
fi

# Change to deploy directory
SCRIPT_DIR=$(dirname $(readlink -f $0))

pushd $SCRIPT_DIR > /dev/null


SSH_TARGET="$1"
REMOTE_DEPLOY_DIR="~/deploy"

# Parse flags
BUILD=true

for arg in "$@"; do
  case $arg in
    --nobuild)
      BUILD=false
      ;;
  esac
done


echo "=== SSH Deploy ==="
echo "Target: $SSH_TARGET"
echo "Remote deploy dir: $REMOTE_DEPLOY_DIR"
echo "Build: $BUILD"
echo ""

# Execute build.sh unless the --nobuild flag is present
if [[ "$BUILD" == "true" ]]; then
  echo "Running build.sh..."
  ./build.sh
fi

# Cleanup remote deployment
echo "Cleaning up remote deployment..."
ssh "$SSH_TARGET" "
    if [ -f $REMOTE_DEPLOY_DIR/down.sh ]; then
        echo 'Running down.sh on remote...'
        cd $REMOTE_DEPLOY_DIR && ./down.sh
    fi
    if [ -d $REMOTE_DEPLOY_DIR ]; then
        echo 'Removing deploy folder...'
        rm -rf $REMOTE_DEPLOY_DIR
    fi
"

# Create remote deploy directory if it doesn't exist
echo "Creating remote deploy directory..."
ssh "$SSH_TARGET" "mkdir -p $REMOTE_DEPLOY_DIR"

# Copy deploy folder contents to remote
echo "Copying deploy folder to remote..."
scp -r ./* "$SSH_TARGET:$REMOTE_DEPLOY_DIR/"

# Make scripts executable on remote
echo "Setting execute permissions on remote scripts..."
ssh "$SSH_TARGET" "chmod +x $REMOTE_DEPLOY_DIR/*.sh"

# Run deploy script on remote
echo ""
echo "Running deployment on remote server..."
ssh "$SSH_TARGET" "cd $REMOTE_DEPLOY_DIR && ./up.sh"

popd > /dev/null

echo ""
echo "=== Deployment Complete ==="
