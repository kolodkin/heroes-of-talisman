#!/bin/bash
set -e

# Build script for Heroes of Talisman
# Builds the frontend SPA, Python wheel, and generates requirements.txt

# Change to project root directory
SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=$SCRIPT_DIR/..
pushd $ROOT_DIR > /dev/null

# Clean up any existing dist directory
rm -rf dist

# Build the frontend using Vite (output goes to dist/ directory)
echo "Building frontend..."
npm run build

# Clean up any existing server/www directory to avoid conflicts
echo "Cleaning server/www directory..."
rm -rf server/www

# Move the built files from dist/ to server/www/
echo "Moving build files to server/www..."
mv dist server/www

# Generate requirements.txt from pyproject.toml
echo "Generating requirements.txt..."
uv pip compile pyproject.toml -o deploy/requirements.txt --no-annotate

# Build Python wheel package (skip sdist to avoid missing generated files)
echo "Building Python wheel..."
rm -rf dist
uv build --wheel

# Copy the generated wheel to deploy folder
echo "Copying wheel to deploy folder..."
rm -f deploy/*.whl
cp dist/*.whl deploy/

# Copy alembic files to deploy folder
echo "Copying alembic files to deploy folder..."
rm -rf deploy/alembic
cp -r alembic deploy/
cp alembic.ini deploy/

# Clean up any existing dist and www directories
rm -rf dist
rm -rf server/www

echo "Build complete!"
echo "  - Frontend files in server/www/"
echo "  - Requirements file: deploy/requirements.txt"
echo "  - Python wheel in deploy/"
echo "  - Alembic files in deploy/"

popd > /dev/null