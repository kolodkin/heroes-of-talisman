#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=$SCRIPT_DIR/..

cd $ROOT_DIR
echo MY_UID=$(id -u) > .env
echo MY_GID=$(id -g) >> .env
echo MY_NODE=$(node --version | sed 's/^v//') >> .env