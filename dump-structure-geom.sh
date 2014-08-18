#!/bin/sh
TOOL='./main'
DATFILE='../bzr/data/client_portal.dat'

$TOOL $DATFILE ls \
    | grep -E '^0d' \
    | cut -f 1 -d ' ' \
    | xargs -d '\n' -n 1 \
    sh dump-structure-geom-inner.sh

