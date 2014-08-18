import struct

__all__ = ['Reader']

def isprint(c):
    return c > 0x1F and c < 0x7F

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
        if val & 0x80:
            val = (val & 0x7F) << 8 | self.readbyte()
        return val

    def dump(self, maxlen=sys.maxsize, perline=32):
        hexpart = ''
        asciipart = ''
        line = ''
        for i in range(min(len(self.data), maxlen)):
            if i != 0 and i % perline == 0:
                print(hexpart, asciipart)
                hexpart = ''
                asciipart = ''
            hexpart = '{} {:02x}'.format(hexpart, self.data[i])
            asciipart = '{}{}'.format(asciipart, chr(self.data[i]) if isprint(self.data[i]) else '.')
        if hexpart:
            while len(hexpart) < perline * 3:
                hexpart = hexpart + '   '
            print(hexpart, asciipart)

    def __len__(self):
        return len(self.data)
