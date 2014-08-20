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
print('numPieces = {}'.format(numPieces))

############
# FIRST PIECE STARTS HERE
############

index = r.readint()
assert index == 0
print('index = {}'.format(index))

numTriangleFans = r.readint()
print('numTriangleFans = {}'.format(numTriangleFans))

numCollisionTriangleFans = r.readint()
print('numCollisionTriangleFans = {}'.format(numCollisionTriangleFans))

numShorts = r.readint()
print('numShorts = {}'.format(numShorts))

unk5 = r.readint()
print('unk5 = {}'.format(unk5))
assert unk5 == 1

numVertices = r.readshort()
print('numVertices = {}'.format(numVertices))

unk6 = r.readshort()
assert unk6 == 0
print('unk6 = {}'.format(unk6))

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
print('unk7 = {}'.format(unk7))

unpack_bsp(r, 0)

############
# SECOND PIECE STARTS HERE
############

index2 = r.readint()
print('index2 = {}'.format(index2))

numTriangleFans2 = r.readint()
print('numTriangleFans2 = {}'.format(numTriangleFans2))

numCollisionTriangleFans2 = r.readint()
print('numCollisionTriangleFans2 = {}'.format(numCollisionTriangleFans2))

numShorts2 = r.readint()
print('numShorts2 = {}'.format(numShorts2))

unk12 = r.readint()
print('unk12 = {}'.format(unk12))

numVertices2 = r.readshort()
print('numVertices2 = {}'.format(numVertices2))

unk13 = r.readshort()
print('unk13 = {}'.format(unk13))

for i in range(numVertices2):
    unpack_vertex(r, i)

for i in range(numTriangleFans2):
    unpack_trifan(r, i)

for i in range(numShorts2):
    r.readshort()
r.align()

unpack_bsp(r, 2)

for i in range(numCollisionTriangleFans2):
    unpack_trifan(r, i)

unpack_bsp(r, 1)

unk14 = r.readint()
print('unk14 = {}'.format(unk14))

unpack_bsp(r, 0)

assert len(r) == 0
