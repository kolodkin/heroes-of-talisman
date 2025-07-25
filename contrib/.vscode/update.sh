#!/bin/bash
mkdir -p $(dirname $0)/../contrib
rsync -av $(dirname $0) $(dirname $0)/../contrib
