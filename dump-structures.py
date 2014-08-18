#!/usr/bin/env python
import struct
import sys
import math

class Reader(object):
    def __init__(self, data):
        self.data = data

    def readbyte(self):
        b = self.data[0]
        self.data = self.data[1:]
        return b

    def readshort(self):
        s, = struct.unpack('H', self.data[:2])
        self.data = self.data[2:]
        return s

    def readint(self):
        i, = struct.unpack('I', self.data[:4])
        self.data = self.data[4:]
        return i

    def readformat(self, fmt):
        size = struct.calcsize(fmt)
        t = struct.unpack(fmt, self.data[:size])
        self.data = self.data[size:]
        return t

    def readraw(self, nbytes):
        b = self.data[:nbytes]
        self.data = self.data[nbytes:]
        return b

    def readvarint(self):
        val = self.readbyte()
        #print("varint: {:02x}".format(val))
        if val & 0x80:
            val = (val & 0x7F) << 8 | self.readbyte()
        return val

    def dump(self, maxlen=-1, perline=32):
        line = ''
        if maxlen == -1:
            maxlen = len(self.data)
        for i in range(min(len(self.data), maxlen)):
            if i != 0 and i % perline == 0:
                print(line)
                line = ''
            line = '{} {:02x}'.format(line, self.data[i])
        if line:
            print(line)

    def __len__(self):
        return len(self.data)

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
    r.readshort()
    r.readshort()
    structId = r.readshort()
    r.readshort()
    #print('connection {}: {:04x}'.format(i, structId))

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
    r.readint()

#r.dump()
assert len(r) == 0

