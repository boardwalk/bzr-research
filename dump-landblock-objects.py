#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())
#r.dump(1024)

fid = r.readint()
assert fid & 0x0000FFFF == 0x0000FFFE

numCells = r.readint()

numObjects = r.readshort()
r.readshort()

for i in range(numObjects):
    modelId = r.readint()
    x, y, z = r.readformat('3f')
    assert x >= 0.0 and x <= 192.0
    assert y >= 0.0 and y <= 192.0
    #assert z >= 0.0 and z <= 512.0
    rw, rx, ry, rz = r.readformat('4f')

numBuildings = r.readshort()
hasthings = r.readshort()

#print('fid = {:08x} numBuildings = {} thing = {}'.format(fid, numBuildings, thing))

for i in range(numBuildings):
    modelId = r.readint()
    x, y, z = r.readformat('3f')
    assert x >= 0.0 and x <= 192.0
    assert y >= 0.0 and y <= 192.0
    #assert z >= 0.0 and z <= 512.0
    rw, rx, ry, rz = r.readformat('4f')
    assert rw >= -1.0 and rw <= 1.0
    assert rx >= -1.0 and rx <= 1.0
    assert ry >= -1.0 and ry <= 1.0
    assert rz >= -1.0 and rz <= 1.0
    numLeaves = r.readint()
    numPortals = r.readint()
    #print('    {} numLeaves = 0x{:08x} numPortals = {}'.format(i, numLeaves, numPortals))
    for j in range(numPortals):
        portalSide = r.readshort()
        otherCellId = r.readshort()
        otherPortalId = r.readshort()
        numStabs = r.readshort()
        #print('        {} portalSide = {} otherCellId = {} otherPortalId = {} numStabs = {}'
        #        .format(j, portalSide, otherCellId, otherPortalId, numStabs))
        for k in range(numStabs):
            stab = r.readshort()
            #print('            {} stab = {}'.format(k, stab))

        r.align()

print('fid = {:08x} remaining = {}'.format(fid, len(r)))

if hasthings:
    numthings = r.readshort()
    unk = r.readshort()
    assert unk == 8
    for i in range(numthings):
        x = r.readint()
        y = r.readint()
        print('  {:08x} {:08x}'.format(x, y))
        if x != 0:
            assert (fid >> 16) == (x >> 16) # matched landblock ids?
            assert (y >> 28) == 0x7
            assert (fid >> 16) == ((y >> 12) & 0xFFFF)
            #assert (x & 0xFFFF) >= 0x100 and (x & 0xFFFF) < 0x100 + numCells

assert len(r) == 0

