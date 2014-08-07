#!/bin/sh
TOOL='./main'
DATFILE='../bzr/data/client_portal.dat'

$TOOL $DATFILE cat $1 \
    | python dump-texture-lookups.py $1

