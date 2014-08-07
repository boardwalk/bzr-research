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

r.dump()

image_id, zero, two, num_palettes = r.readformat('=IIBI')
palettes = [r.readint() for i in range(num_palettes)]

print("{:08x} {} {} {}".format(image_id, zero, two, num_palettes))

print( ' '.join(['{:08x}'.format(p) for p in palettes]) )
#print(palettes)

assert zero == 0
assert two == 2
assert len(r) == 0

#r.dump(1024)

#print("-----")

