#!/bin/sh
TOOL='./main'
DATFILE='../bzr/data/client_portal.dat'
set -e -x

$TOOL $DATFILE cat $1 \
    | python dump-physics-script.py

