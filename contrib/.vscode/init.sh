#!/bin/bash
mkdir -p $(dirname $0)/../../.vscode
rsync -av $(dirname $0) $(dirname $0)/../../.vscode
