#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=$SCRIPT_DIR/..

if [ -f $ROOT_DIR/.env.tmp ]; then
    set +o allexport
    source $ROOT_DIR/.env.tmp
    set -o allexport
fi

cd $ROOT_DIR
echo MY_UID=$(id -u) > .env
echo MY_GID=$(id -g) >> .env
echo MY_NODE=$(node --version | sed 's/^v//') >> .env

echo "" >> .env
echo "# POSTGRES" >> .env
echo POSTGRES_HOST=${POSTGRES_HOST:-localhost} >> .env
echo POSTGRES_USER=${POSTGRES_USER:-postgres} >> .env
echo POSTGRES_PORT=${POSTGRES_PORT:-5432} >> .env
echo POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres} >> .env
echo POSTGRES_DB=${POSTGRES_DB:-postgres} >> .env

echo "" >> .env
echo "# REDIS" >> .env
echo REDIS_HOST=${REDIS_HOST:-localhost} >> .env
echo REDIS_PORT=${REDIS_PORT:-6379} >> .env
echo REDIS_PASSWORD=${REDIS_PASSWORD:-redis} >> .env

echo "" >> .env
echo "# APP" >> .env
echo APP_PORT=${APP_PORT:-8000} >> .env

echo "" >> .env
echo "# WWW" >> .env
echo WWW_PORT=${WWW_PORT:-5173} >> .env

echo "" >> .env
echo "# PLAYWRIGHT" >> .env
echo PLAYWRIGHT_REPORT_PORT=${PLAYWRIGHT_REPORT_PORT:-9323} >> .env
echo PLAYWRIGHT_SINGLE_PROCESS=${PLAYWRIGHT_SINGLE_PROCESS:-false} >> .env
