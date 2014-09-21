import struct
import sys

__all__ = ['Reader']

def isprint(c):
    return c > 0x1F and c < 0x7F

class Reader(object):
    def __init__(self, data):
        self.data = data
        self.position = 0

    def peekformat(self, fmt, offset):
        size = struct.calcsize(fmt)
        t = struct.unpack(fmt, self.data[self.position + offset : self.position + offset + size])
        return t if len(t) > 1 else t[0]

    def readformat(self, fmt):
        size = struct.calcsize(fmt)
        t = struct.unpack(fmt, self.data[self.position : self.position + size])
        self.position += size
        return t if len(t) > 1 else t[0]

    def readbyte(self):
        return self.readformat('B')

    def readshort(self):
        return self.readformat('H')

    def readint(self):
        return self.readformat('I')

    def readfloat(self):
        return self.readformat('f')

    def readvarint(self):
        val = self.readbyte()
        if val & 0x80:
            val = (val & 0x7F) << 8 | self.readbyte()
        return val

    def align(self):
        while self.position % 4 != 0:
            self.position += 1

    def skip(self, size):
        self.position += size
        assert self.position <= len(self.data)

    def raw(self):
        return self.data[self.position :]

    def dump(self, maxlen=sys.maxsize, perline=32):
        hexpart = ''
        asciipart = ''
        line = ''
        for i in range(min(len(self), maxlen)):
            if i != 0 and i % perline == 0:
                print(hexpart, asciipart)
                hexpart = ''
                asciipart = ''
            hexpart = '{} {:02x}'.format(hexpart, self.data[self.position + i])
            asciipart = '{}{}'.format(asciipart, chr(self.data[self.position + i]) if isprint(self.data[self.position + i]) else '.')
        if hexpart:
            while len(hexpart) < perline * 3:
                hexpart = hexpart + '   '
            print(hexpart, asciipart)

    def __len__(self):
        return len(self.data) - self.position
