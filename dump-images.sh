#!/bin/sh
TOOL='./main'
DATFILE='../bzr/data/client_portal.dat'

$TOOL $DATFILE ls \
    | grep -E '^06' \
    | cut -f 1 -d ' ' \
    | xargs -d '\n' -n 1 -P 4 \
    sh dump-images-inner.sh

