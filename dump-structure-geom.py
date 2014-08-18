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

fid = r.readint()
assert fid & 0xFF000000 == 0x0D000000

unk1 = r.readint()
print('unk1 = {}'.format(unk1))
assert unk1 == 1 or unk1 == 2 or unk1 == 3

unk2 = r.readint()
assert unk2 == 0

numTriangleStrips = r.readint()
print('numTriangleStrips: {}'.format(numTriangleStrips))

unk3 = r.readint()
print('unk3 = {}'.format(unk3))
#assert unk3 == 0x32

unk4 = r.readint()
print('unk4 = {}'.format(unk4))

unk5 = r.readint()
assert unk5 == 1

numVertices = r.readshort()
print('numVertices: {}'.format(numVertices))

unk6 = r.readshort()
assert unk6 == 0

for i in range(numVertices):
    vertexnum = r.readshort()
    assert vertexnum == i

    ntexcoord = r.readshort()

    vx, vy, vz = r.readformat('3f')

    assert abs(vx) < 15000.0 and abs(vy) < 15000.0 and abs(vz) < 15000.0

    nx, ny, nz = r.readformat('3f')
    mag_n = math.sqrt(nx * nx + ny * ny + nz * nz)
    assert (mag_n >= 0.99 and mag_n <= 1.01) or mag_n == 0.0

    for j in range(ntexcoord):
        s, t = r.readformat('2f')
        # AC does seem to use texture wrapping, so no assert [0-1] here
        #if s < 0.0 or s > 10.0:
        #    print('s out of range: {}'.format(s))
        #if t < 0.0 or t > 10.0:
        #    print('t out of range: {}'.format(t))

for i in range(numTriangleStrips):
    primnum = r.readshort()
    assert primnum == i

    numindices = r.readbyte()
    primflags = r.readbyte()
    primflags2 = r.readint()
    assert primflags in [0x00, 0x01, 0x04]
    assert primflags2 in [0x00, 0x01, 0x02]

    texnum = r.readshort()
    r.readshort()

    print('texnum = {:x}'.format(texnum))

    for i in range(numindices):
        vertindex = r.readshort()

    if primflags != 0x04:
        for i in range(numindices):
            r.readbyte()

    if primflags2 == 0x02:
        for i in range(numindices):
            r.readbyte()

print('remaining: {}'.format(len(r)))
