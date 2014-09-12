#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

def parse_anim(r):
    iden = r.readshort()
    stance = r.readshort()
    numanims = r.readbyte()
    d = r.readbyte()
    e = r.readbyte()
    f = r.readbyte()

    #print('id = {:04x} stance = {:04x} numanims = {:02x} {:02x} {:02x} {:02x}'.
    #        format(iden, stance, numanims, d, e, f))

    for j in range(numanims):
        animid = r.readint()
        firstframe = r.readint()
        lastframe = r.readint()
        playspeed = r.readfloat()
        #print('  {} animid = {:08x} firstframe = {:08x} lastframe = {:08x} playspeed = {:.2f}'.format(j, animid, firstframe, lastframe, playspeed))
        assert animid & 0xFF000000 == 0x03000000
        assert animid & 0x00FFFFFF < 0x5000

    if e == 0x01 or e == 0x02:
        a = r.readfloat()
        b = r.readfloat()
        c = r.readfloat()
        #print("a = {:.2f} b = {:.2f} c = {:.2f}".format(a, b, c))

    #assert stance in [0x3C, 0x3D, 0x3E, 0x3F, 0x41, 0x40, 0x44, 0x46, 0x47, 0x49, 0xE8, 0xE9, 0x138, 0x139, 0x1000]
    assert d == 0 or d == 1 or d == 2
    assert e == 0 or e == 1 or e == 2
    assert f == 0

fid = r.readint()
assert fid & 0xFF000000 == 0x09000000

print('=== fid = {:08x}'.format(fid))

unk1 = r.readint()
count1 = r.readint()

for i in range(count1):
    r.readint()
    r.readint()

count2 = r.readint()

#print("Strips 1: {}".format(count2))

for i in range(count2):
    parse_anim(r)

count3 = r.readint()

#print("Strips 2: {}".format(count3))

for i in range(count3):
    parse_anim(r)

count4 = r.readint()

for i in range(count4):
    unk = r.readint()
    count5 = r.readint()
    #print("Combo strip: {}, unk = {:x}".format(i, unk))
    for j in range(count5):
        parse_anim(r)

assert len(r) == 0

