#!/bin/sh
TOOL='./main'
DATFILE='../bzr/data/client_cell_1.dat'

$TOOL $DATFILE cat $1 \
    | python dump-structures.py

