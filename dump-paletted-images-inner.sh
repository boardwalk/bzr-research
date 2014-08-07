#!/bin/sh
set -e
TOOL='./main'
DATFILE='../bzr/data/client_portal.dat'

$TOOL $DATFILE cat $1 \
    | python dump-paletted-images.py

