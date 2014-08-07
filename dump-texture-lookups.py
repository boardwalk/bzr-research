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

    def dump(self, maxlen=-1):
        line = ''
        for i in range(min(len(self.data), maxlen)):
            if i != 0 and i % 32 == 0:
                print(line)
                line = ''
            line = '{} {:02x}'.format(line, self.data[i])
        if line:
            print(line)

    def __len__(self):
        return len(self.data)

r = Reader(sys.stdin.buffer.raw.read())
#r.dump(1024)

flags = r.readint()

print("{} {:08x}".format(sys.argv[1], flags))

if flags & 0x01:
    thingie = r.readint()
    #print('thingie = {:08x}'.format(thingie))

if flags & 0x02 or flags & 0x04:
    textureId = r.readint()
    zero = r.readint()
    assert zero == 0
    #print('textureId = {:08x}'.format(textureId))

s, = r.readformat('f')
t, = r.readformat('f')
p, = r.readformat('f')

if flags & 0x10:
    assert s != 0.0
else:
    assert s == 0.0

assert len(r) == 0

#print('floats = {}, {}, {}'.format(s, t, p))

#
# 00000001 [thing including FF]           00000000  [a float] [a float]
# 00000002 [texture id]         00000000  00000000  [a float] [a float]
# 00000004 [texture id]         00000000  00000000  [a float] [a float]

# 00000011 [thing including FF]           [a float] [a float] [a float]
# 00000012 [texture id]         00000000  [a float] [a float] [a float]
# 00000014 [texture id]         00000000  [a float] [a float] [a float]
#

# ... & 1    has thing
# ... & 2    has texture id, 00000000
# ... & 4    has texture id, 00000000
# ... & 10   first float not zero

