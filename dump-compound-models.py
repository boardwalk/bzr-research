#!/usr/bin/env python
import sys
import math
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x02000000

flags = r.readint()
assert flags <= 0xF

numParts = r.readint()

print('=== fid: {:08x}, flags: {:x}, numParts: {}'.format(fid, flags, numParts))

def read_location(r):
    x, y, z = r.readformat('3f')
    rw, rx, ry, rz = r.readformat('4f')
    mag = math.sqrt(rw*rw + rx*rx + ry*ry + rz*rz)
    assert mag >= 0.999 and mag <= 1.001

for i in range(numParts):
    modelid = r.readint()
    #print('{:02x} submodel: {:08x}'.format(i, modelid))
    assert modelid & 0xFF000000 == 0x01000000

if flags & 1:
    for i in range(numParts):
        parent = r.readint()
        #print('{:02x} parent: {:08x}'.format(i, parent))
        assert parent < numParts or parent == 0xFFFFFFFF

if flags & 2:
    for i in range(numParts):
        sx, sy, sz = r.readformat('3f')

numHoldLocations = r.readint()

for i in range(numHoldLocations):
    key = r.readint()
    partId = r.readint()
    read_location(r)

numConnectionPoints = r.readint()
assert numConnectionPoints == 0

for i in range(numConnectionPoints):
    key = r.readint()
    partId = r.readint()
    read_location(r)

numPlacementFrames = r.readint()
assert numPlacementFrames >= 0x01 and numPlacementFrames <= 0x13

for i in range(numPlacementFrames):
    key = r.readint()
    for j  in range(numParts):
        read_location(r)
    x = r.readint() # ????
    assert x == 0

numCylSphere = r.readint()

for i in range(numCylSphere):
    x, y, z = r.readformat('fff')
    radius, h = r.readformat('ff')

numSphere = r.readint()

for i in range(numSphere):
    x, y, z = r.readformat('fff')
    radius = r.readformat('f')

height = r.readfloat()
radius = r.readfloat()
stepUpHeight = r.readfloat()
stepDownHeight = r.readfloat()

# sorting sphere
r.readformat('fff')
r.readformat('f')

# selection sphere
r.readformat('fff')
r.readformat('f')

numLights = r.readint()

for i in range(numLights):
    lightIndex = r.readint()
    assert lightIndex == i
    read_location(r)
    color = r.readint()
    intensity = r.readfloat()
    falloff = r.readfloat()
    coneangle = r.readfloat() # junk 0xcdcdcdcd most of the time

defaultAnimId = r.readint()
defaultScriptId = r.readint()
defaultMTableId = r.readint()
defaultStableId = r.readint()
defaultPhstableId = r.readint()

assert len(r) == 0

