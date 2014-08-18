#!/usr/bin/env python
import sys
from reader import Reader

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


