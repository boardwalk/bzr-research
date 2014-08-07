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
assert fid & 0xFF000000 == 0x01000000

flags = r.readint()
assert flags == 0x2 or flags == 0x3 or flags == 0xA or flags == 0xB
#print('flags: {:08x}'.format(flags))

ntex = r.readbyte()
tex = [r.readint() for i in range(ntex)]
#print('ntex = {}'.format(ntex))

one = r.readint()
assert one == 1

nvert = r.readshort()
#print("nvert = {}".format(nvert))

unk2 = r.readshort()
assert unk2 == 0x0000 or unk2 == 0x0800
#print('unk2: {:04x}'.format(unk2))

for i in range(nvert):
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

#r.dump(512)

if flags == 0x02 or flags == 0xA: # & 0x2 should suffice
    unk2x, unk2y, unk2z = r.readformat('3f')
    #print('{} {} {}'.format(unk2x, unk2y, unk2z))

nprim = r.readvarint()


for i in range(nprim):
    #print('on prim {}'.format(i))
    #r.dump(64)

    primnum = r.readshort()
    assert primnum == i

    numindices = r.readbyte()
    primflags = r.readbyte()
    primflags2 = r.readbyte()

    #bytesperindex = 3
    #extrabytes = 0

    if primflags == 0x00:
        pass
    elif primflags == 0x01:
        pass
    elif primflags == 0x04: # no texture num?
        #bytesperindex = 2
        pass
    else:
        assert False

    #print("primflags2 = {}".format(primflags2))

    if primflags2 == 0x00:
        pass
    elif primflags2 == 0x01:
        pass
    elif primflags2 == 0x02:
        #extrabytes += numindices
        pass
    else:
        assert False

    #nbytes = numindices * bytesperindex + extrabytes

    #for i in range(nbytes):
    #    r.readbyte()

    # i dunno wtf this stuff is!
    r.readbyte()
    r.readbyte()
    r.readbyte()
    r.readbyte()
    r.readbyte()
    r.readbyte()
    r.readbyte()

    #print('  i={}'.format(i))

    for i in range(numindices):
        vertindex = r.readshort()
        #print('    vertindex: {}'.format(vertindex))

    for i in range(numindices):
        if primflags == 0x04:
            texnum = 0x00
        else:
            texnum = r.readbyte()
        #print('    texnum: {}'.format(texnum))

    if primflags2 == 0x02:
        for i in range(numindices):
            r.readbyte()

print('fid = {:08x}h nvert = {:04x}h nprim = {:04x}h remaining = {}'.format(fid, nvert, nprim, len(r)))

#print('float: {}'.format(r.readformat('ff')))

r.dump(2048, 52)

