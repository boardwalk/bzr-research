#!/usr/bin/env python
import sys
import math
from reader import Reader
from bsp import unpack_bsp
from model import unpack_vertex, unpack_trifan

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x0D000000

numPieces = r.readint()
print('{:08x} numPieces = {}'.format(fid, numPieces))

for pi in range(numPieces):
    #print('======')

    pieceIndex = r.readshort()
    #print('pieceIndex = {}'.format(pieceIndex))
    assert pieceIndex == pi

    unk4 = r.readshort()
    #print('unk4 = {}'.format(unk4))
    assert unk4 == 0

    numTriangleFans = r.readint()
    #print('numTriangleFans = {}'.format(numTriangleFans))

    numCollisionTriangleFans = r.readint()
    #print('numCollisionTriangleFans = {}'.format(numCollisionTriangleFans))

    numShorts = r.readint()
    #print('numShorts = {}'.format(numShorts))

    unk5 = r.readint()
    #print('unk5 = {}'.format(unk5))
    assert unk5 == 1

    numVertices = r.readshort()
    #print('numVertices = {}'.format(numVertices))

    unk6 = r.readshort()
    #print('unk6 = {}'.format(unk6))
    assert unk6 == 0

    for i in range(numVertices):
        unpack_vertex(r, i)

    for i in range(numTriangleFans):
        unpack_trifan(r, i)

    for i in range(numShorts):
        r.readshort()
    r.align()

    unpack_bsp(r, 2)

    for i in range(numCollisionTriangleFans):
        unpack_trifan(r, i)

    unpack_bsp(r, 1)

    unk7 = r.readint()
    #print('unk7 = {}'.format(unk7))
    assert unk7 == 0 or unk7 == 1

    if unk7:
        unpack_bsp(r, 0)

    r.align()

assert len(r) == 0
