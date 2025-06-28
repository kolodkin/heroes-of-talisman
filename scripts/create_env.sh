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
echo POSTGRES_PORT=${POSTGRES_PORT:-5432} >> .env