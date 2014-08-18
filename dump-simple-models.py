#!/usr/bin/env python
import sys
import math
from reader import Reader
from bsp import unpack_bsp

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
