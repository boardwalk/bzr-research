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

fid = r.readint()
assert fid & 0xFF000000 == 0x02000000

#r.dump(64, 64)

flags = r.readint()
assert flags <= 0xF

if flags != 0xF:
    sys.exit(0)

#if flags == 0x4:
#    r.dump(128)

nummodels = r.readint()

for i in range(nummodels):
    modelid = r.readint()
    assert modelid & 0xFF000000 == 0x01000000

if flags & 1:
    for i in range(nummodels):
        parent = r.readint()
        assert parent < nummodels or parent == 0xFFFFFFFF

if flags & 2:
    for i in range(nummodels):
        r.readint()
        r.readint()
        r.readint()

unk1 = r.readint()
unk2 = r.readint()
unk3 = r.readint()
unk4 = r.readint()

print("{:08x} {:08x} {:08x} {:08x} fid={:08x} flags={:02X}".format(unk1, unk2, unk3, unk4, fid, flags))

#assert unk1 == 0
#assert unk2 == 0
#assert unk3 == 1
#assert unk4 == 0

for i in range(nummodels):
    #pass
    x, y, z = r.readformat('fff')
    print("pos: {} {} {}".format(x, y, z))

    w, x, y, z = r.readformat('ffff')
    print("rot: {} {} {} {}".format(w, x, y, z))

#print("ok!")
#r.dump()


