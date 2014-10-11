#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

#r.dump()

resourceId = r.readint()

flags = r.readint()

print("resourceId = {:08x} flags = {:x}".format(resourceId, flags))

assert flags == 0 or flags == 2

resourceId2 = r.readint()

numTextures = r.readbyte()

numConnections = r.readbyte()

numVisible = r.readshort()

for i in range(numTextures):
    textureId = r.readshort()
    #print('texture {}: {:04x}'.format(i, textureId))

#r.align()

geometryId = r.readint()
#print('geometryId={:08x}'.format(geometryId))

x, y, z = r.readformat('fff')
rw, rx, ry, rz = r.readformat('ffff')

#print('x={}, y={}, z={}'.format(x, y, z))
#print('rw={}, rx={}, ry={}, rz={}'.format(rw, rx, ry, rz))

for i in range(numConnections):
    a = r.readshort()
    b = r.readshort()
    structId = r.readshort()
    c = r.readshort()
    #print('connection {}: {:04x} {:04x} {:04x} {:04x}'.format(i, a, b, structId, c))

for i in range(numVisible):
    structId = r.readshort()
    #print('visible {}: {:04x}'.format(i, structId))

if flags & 2:
    numObjects = r.readint()
    #print('numObjects {:08x}'.format(numObjects))

    for i in range(numObjects):
        modelId = r.readint()
        x, y, z = r.readformat('fff')
        rw, rx, ry, rz = r.readformat('ffff')
        #print('modelId={:08x}'.format(modelId))
        #print('x={}, y={}, z={}'.format(x, y, z))
        #print('rw={}, rx={}, ry={}, rz={}'.format(rw, rx, ry, rz))


if flags & 8:
    a = r.readint()
    print('restriction obj: {:08x}'.format(a))

#r.dump()
assert len(r) == 0

