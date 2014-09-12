#!/usr/bin/env python
import sys
import math
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x02000000

flags = r.readint()
assert flags <= 0xF

nummodels = r.readint()

#print('=== fid: {:08x}, flags: {:x}, nummodels: {}'.format(fid, flags, nummodels))

for i in range(nummodels):
    modelid = r.readint()
    #print('{:02x} submodel: {:08x}'.format(i, modelid))
    assert modelid & 0xFF000000 == 0x01000000

if flags & 1:
    for i in range(nummodels):
        parent = r.readint()
        #print('{:02x} parent: {:08x}'.format(i, parent))
        assert parent < nummodels or parent == 0xFFFFFFFF

if flags & 2:
    for i in range(nummodels):
        sx, sy, sz = r.readformat('3f')
        #print('{:02x} scale: {}, {}, {}'.format(i, sx, sy, s))

numExtendedLocs = r.readint()

for i in range(numExtendedLocs):
    s = r.readint()
    t = r.readint()
    x, y, z = r.readformat('fff')
    rw, rx, ry, rz = r.readformat('ffff')
    #print("{:02x} s: {} t: {} pos: {:.2f} {:.2f} {:.2f} rot: {:.2f} {:.2f} {:.2f} {:.2f}".format(i, s, t, x, y, z, rw, rx, ry, rz))
    mag = math.sqrt(rw*rw + rx*rx + ry*ry + rz*rz)
    assert mag >= 0.999 and mag <= 1.001

unk1 = r.readint()
assert unk1 == 0
unk2 = r.readint()
assert unk2 >= 0x01 and unk2 <= 0x13
unk3 = r.readint()
assert unk3 <= 0xf0

for i in range(nummodels):
    x, y, z = r.readformat('fff')
    rw, rx, ry, rz = r.readformat('ffff')
    #print("{:02x} pos: {:.2f} {:.2f} {:.2f} rot: {:.2f} {:.2f} {:.2f} {:.2f}".format(i, x, y, z, rw, rx, ry, rz))
    mag = math.sqrt(rw*rw + rx*rx + ry*ry + rz*rz)
    assert mag >= 0.999 and mag <= 1.001

unk4 = r.readint()
assert unk4 == 0

#print('flags = {:x} unk2 = {:08x} unk3 = {:08x}'.format(flags, unk2, unk3))

#unk5 = r.readint()
#unk6 = r.readint()

#unk7 = r.readfloat()
#unk8 = r.readfloat()
#unk9 = r.readfloat()

#assert unk7 >= -10.0 and unk7 <= 10.0
#assert unk8 >= -10.0 and unk8 <= 10.0
#assert unk9 >= -10.0 and unk9 <= 10.0

#assert unk7 == 0
#assert unk8 == 0
#assert unk9 == 0

#found_at_offset = -1

#for offset in range(0, len(r) - 4, 4):
#    x = r.peekformat('I', offset)
#    if (x & 0xFF000000) == 0x03000000:
#        found_at_offset = offset
#        break

anim_id = r.peekformat('I', len(r) - 20)
animset_id = r.peekformat('I', len(r) - 14)

assert(anim_id == 0 or (anim_id & 0xFF000000) == 0x03000000)
#assert(animset_id == 0 or (animset_id & 0xFF000000) == 0x09000000)

if animset_id != 0:
    print('animset_id = {:08x}'.format(animset_id))

#found_at_offset = len(r) - 12
#x = r.peekformat('I', found_at_offset)

#if True:
#if found_at_offset >= 0:
#    print('=== fid: {:08x}, flags: {:x}, nummodels: {}'.format(fid, flags, nummodels))
    #print('unk2 = {:08x} unk3 = {:08x}'.format(unk2, unk3))
    #print('unk6 = {:08x} flags = {:01x} unk2 = {:08x} unk3 = {:08x} unk5 = {:08x}'.format(unk6, flags, unk2, unk3, unk5))
    #print('unk7 = {:.2f} unk8 = {:.2f} unk9 = {:.2f}'.format(unk7, unk8, unk9))
    #print("anim = {:08x} at offset = {}".format(x, found_at_offset))
    #print("remaining: {}".format(len(r)))
    #r.dump()


