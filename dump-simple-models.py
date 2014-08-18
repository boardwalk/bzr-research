#!/usr/bin/env python
import struct
import sys
import math

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

def unpack_trifan(r):
    nprim = r.readvarint()
    for i in range(nprim):
        primnum = r.readshort()
        assert primnum == i

        numindices = r.readbyte()
        primflags = r.readbyte()
        assert primflags in [0x00, 0x01, 0x04]
        primflags2 = r.readint()
        assert primflags2 in [0x00, 0x01, 0x02]
        texIndex = r.readshort()
        r.readshort()

        for i in range(numindices):
            vertindex = r.readshort()

        if primflags != 0x04:
            for i in range(numindices):
                texCoordIndex = r.readbyte()

        if primflags2 == 0x02:
            for i in range(numindices):
                r.readbyte()

indent = 0

def unpack_bsp(r, tree_type):
    global indent
    indent += 1
    bsp_type = r.readint()
    if bsp_type == 0x4c454146: # LEAF
        #print(' ' * indent + "LEAF ENTER")
        unpack_bsp_leaf(r, tree_type)
        #print(' ' * indent + "LEAF LEAVE")
    elif bsp_type == 0x504f5254: # PORT
        #print(' ' * indent + "PORT ENTER")
        unpack_bsp_portal(r, tree_type)
        #print(' ' * indent + "PORT LEAVE")
    else:
        #print(' ' * indent + "NODE ENTER")
        unpack_bsp_node(r, tree_type, bsp_type)
        #print(' ' * indent + "NODE LEAVE")
    indent -= 1

def unpack_bsp_leaf(r, tree_type):
    r.readint()

    if tree_type != 1:
        return

    notempty = r.readint()

    x, y, z, radius = r.readformat('4I')

    index_count = r.readint()
    for i in range(index_count):
        r.readshort()

    if notempty:
        assert x != 0xcdcdcdcd
        assert y != 0xcdcdcdcd
        assert z != 0xcdcdcdcd
        assert radius != 0xcdcdcdcd
        assert index_count != 0
    else:
        assert x == 0xcdcdcdcd
        assert y == 0xcdcdcdcd
        assert z == 0xcdcdcdcd
        assert radius == 0xcdcdcdcd
        assert index_count == 0

def unpack_bsp_portal(r, tree_type):
    x, y, z, d = r.readformat('4f')

    unpack_bsp(r, tree_type)
    unpack_bsp(r, tree_type)

    if tree_type != 0:
        return

    x, y, z, radius = r.readformat('4f')

    tricount = r.readint()
    polycount = r.readint()

    for i in range(tricount):
        r.readshort()

    for i in range(polycount):
        r.readshort()
        r.readshort()

def unpack_bsp_node(r, tree_type, node_type):
    x, y, z, dist = r.readformat('4f')
    #print(' ' * indent + "plane: {}, {}, {}, {}".format(x, y, z, dist))

    if node_type == 0x42506e6e or node_type == 0x4250496e: # BPnn, BPIn
        #print(' ' * indent + "(BPnn, BPIn)")
        unpack_bsp(r, tree_type)
    elif node_type == 0x4270494e or node_type == 0x42706e4e: # BpIN, BpnN
        #print(' ' * indent * "(BpIN, BpnN)")
        unpack_bsp(r, tree_type)
    elif node_type == 0x4250494e or node_type == 0x42506e4e: # BPIN, BPnN
        #print(' ' * indent + "(BPIN, BPnN)")
        unpack_bsp(r, tree_type)
        unpack_bsp(r, tree_type)
    else:
        #print("node_type = {:08x}".format(node_type))
        pass

    if tree_type == 0 or tree_type == 1:
        x, y, z, radius = r.readformat('4f')
        #print(' ' * indent + "bounds: {}, {}, {}, {}".format(x, y, z, radius))

    if tree_type != 0:
        return

    index_count = r.readint()
    for i in range(index_count):
        r.readshort()

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x01000000
print('fid = {:08x}'.format(fid))

flags = r.readint()
assert flags == 0x2 or flags == 0x3 or flags == 0xA or flags == 0xB
print('flags = {:08x}'.format(flags))

ntex = r.readbyte()
tex = [r.readint() for i in range(ntex)]

one = r.readint()
assert one == 1

nvert = r.readshort()

unk2 = r.readshort()
assert unk2 == 0x0000 or unk2 == 0x0800

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

if flags == 0x02 or flags == 0xA: # & 0x2 should suffice
    unk2x, unk2y, unk2z = r.readformat('3f')


if flags & 1:
    unpack_trifan(r)
    #print("BEFORE")
    #r.dump()
    unpack_bsp(r, 1)
    #print("AFTER")
    #r.dump()


if flags == 3 or flags == 0xB:
    r.readformat('3f')

#r.dump()
if flags & 2:
    unpack_trifan(r)
    unpack_bsp(r, 0)

if flags & 8:
    r.readint()

if len(r) != 0:
    r.dump()
    assert False

print('fid = {:08x}h nvert = {:04x}h remaining = {}'.format(fid, nvert, len(r)))

"""
if flags == 0xA:
    r.dump(1024)

    r.readint()

    r.readint()
    r.readint()
    r.readint()
    r.readint()

    r.readint()
    r.readint()
    r.readint()
    r.readint()

    nthings = r.readint()

    for i in range(nthings):
        r.readshort()

    r.readshort()
    r.readshort()

    assert len(r) == 0
"""
