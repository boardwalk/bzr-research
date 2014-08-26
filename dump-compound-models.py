#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x02000000

flags = r.readint()
assert flags <= 0xF

nummodels = r.readint()

print('=== fid: {:08x}, flags: {:x}, nummodels: {}'.format(fid, flags, nummodels))

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

#unk1 = r.readint()
#unk2 = r.readint()
#unk3 = r.readint()
#unk4 = r.readint()
#print('unks: {:08x} {:08x} {:08x} {:08x}'.format(unk1, unk2, unk3, unk4))

#i = 0
#lastfind = -7*4
#numfound = 0
#
#while len(r) >= i + 7 * 4:
#    x, y, z, rw, rx, ry, rz = struct.unpack('7f', r.data[i: i + 7 * 4])
#
#    if abs(rw) > 100.0 or abs(rx) > 100.0 or abs(ry) > 100.0 or abs(rz) > 100.0:
#        i += 1
#        continue
#
#    mag = math.sqrt(rw*rw + rx*rx + ry*ry + rz*rz)
#    if mag > 0.9999 and mag < 1.0001:
#
#        beforebytes = ''
#        for bi in range(lastfind + 7 * 4, i + 7 * 4):
#            beforebytes = '{} {:02x}'.format(beforebytes, r.data[bi])
#        if beforebytes: print(beforebytes)
#
#        print('{:02x} i:{:04x} p:{:+.3f} {:+.3f} {:+.3f} r:{:+.3f} {:+.3f} {:+.3f} {:+.3f} mag={:f} step={:+d}'.format(numfound, i, x, y, z, rw, rx, ry, rz, mag, i - lastfind))
#        #print('   {:08x} {:08x} {:08x}'.format(*struct.unpack('3I', r.data[0: 3 * 4])))
#        lastfind = i
#        numfound += 1
#
#    i += 1

numExtendedLocs = r.readint()

#if numExtendedLocs != 0:
#    print('foo!')

for i in range(numExtendedLocs):
    s = r.readint()
    t = r.readint()
    x, y, z = r.readformat('fff')
    rw, rx, ry, rz = r.readformat('ffff')
    print("{:02x} s: {} t: {} pos: {:.2f} {:.2f} {:.2f} rot: {:.2f} {:.2f} {:.2f} {:.2f}".format(i, s, t, x, y, z, rw, rx, ry, rz))
    mag = math.sqrt(rw*rw + rx*rx + ry*ry + rz*rz)
    assert mag >= 0.999 and mag <= 1.001

unk1 = r.readint()
assert unk1 == 0
unk2 = r.readint()
#assert unk2 == 1
unk3 = r.readint()
#assert unk3 == 0
print('unk2 = {}, unk3 = {}'.format(unk2, unk3))

#print('===')

for i in range(nummodels):
    x, y, z = r.readformat('fff')
    rw, rx, ry, rz = r.readformat('ffff')
    #print("{:02x} pos: {:.2f} {:.2f} {:.2f} rot: {:.2f} {:.2f} {:.2f} {:.2f}".format(i, x, y, z, rw, rx, ry, rz))
    mag = math.sqrt(rw*rw + rx*rx + ry*ry + rz*rz)
    assert mag >= 0.999 and mag <= 1.001

#for i in range(nummodels):
#    a, b, c = r.readformat('fff')
#    print("{:02x} a, b, c: {:.2f} {:.2f} {:.2f}".format(i, a, b, c))

r.dump(perline=64)
#print('remaining: {}, bytes per model: {}'.format(len(r), float(len(r)) / float(nummodels)))


