#!/bin/sh
TOOL='./main'
DATFILE='../bzr/data/client_cell_1.dat'

$TOOL $DATFILE ls \
    | grep -E '^....fffe' \
    | cut -f 1 -d ' ' \
    | xargs -d '\n' -n 1 \
    sh dump-landblock-objects-inner.sh

