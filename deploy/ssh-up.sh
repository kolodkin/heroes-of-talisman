#!/bin/bash

# SSH Deploy Script
# Usage: ./deploy/ssh-deploy.sh user@host

set -e

# Check if SSH connection string is provided
if [ -z "$1" ]; then
    echo "Error: SSH connection string required"
    echo "Usage: $0 user@host"
    exit 1
fi

SSH_TARGET="$1"
DEPLOY_DIR="deploy"
REMOTE_DEPLOY_DIR="~/deploy"

# Parse flags
BUILD=false

for arg in "$@"; do
  case $arg in
    --build)
      BUILD=true
      ;;
  esac
done


echo "=== SSH Deploy ==="
echo "Target: $SSH_TARGET"
echo "Local deploy dir: $DEPLOY_DIR"
echo "Remote deploy dir: $REMOTE_DEPLOY_DIR"
echo "Build: $BUILD"
echo ""

# Check if deploy directory exists locally
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "Error: Deploy directory '$DEPLOY_DIR' not found"
    exit 1
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
scp -r "$DEPLOY_DIR"/* "$SSH_TARGET:$REMOTE_DEPLOY_DIR/"

# Make scripts executable on remote
echo "Setting execute permissions on remote scripts..."
ssh "$SSH_TARGET" "chmod +x $REMOTE_DEPLOY_DIR/*.sh"

# Run deploy script on remote
echo ""
echo "Running deployment on remote server..."
ssh "$SSH_TARGET" "cd $REMOTE_DEPLOY_DIR && ./up.sh"

echo ""
echo "=== Deployment Complete ==="
