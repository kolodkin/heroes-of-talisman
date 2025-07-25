#!/bin/bash
mkdir -p $(dirname $0)/../../.cursor
rsync -av $(dirname $0) $(dirname $0)/../..
