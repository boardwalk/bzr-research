#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
anim_type = r.readint()
num_parts = r.readint()
num_frames = r.readint()

#print('=== fid = {:08x}'.format(fid))

if anim_type == 1 or anim_type == 3:
    for i in range(num_frames):
        r.readformat('7I') # there are floats in here

for i in range(num_frames):
    #print("on frame {}".format(i))
    for j in range(num_parts):
        x, y, z = r.readformat('3f')
        rw, rx, ry, rz = r.readformat('4f')
    extra_count = r.readint()
    for j in range(extra_count):
        extra_type = r.readint()
        if extra_type == 0x01:
            a = r.readformat('I')
            b = r.readformat('I')
            assert a == 0
            assert (b & 0xFF000000) == 0x0A000000
        elif extra_type == 0x02:
            a = r.readformat('I')
            b = r.readformat('I')
            assert a == 0 or a == 1 or a == 0xFFFFFFFF
            assert b <= 0xFF
        elif extra_type == 0x03:
            r.readformat('8I')
        elif extra_type == 0x05:
            r.readformat('2I')
        elif extra_type == 0x06:
            r.readformat('2I')
        elif extra_type == 0x07:
            r.readformat('5I')
        elif extra_type == 0x0D:
            r.readformat('11I')
        elif extra_type == 0x0F:
            r.readformat('2I')
        elif extra_type == 0x11:
            r.readformat('I')
        elif extra_type == 0x13:
            a = r.readformat('I')
            assert a == 0 or a == 1 or a == 0xFFFFFFFF
            b = r.readformat('I')
            assert b & 0xFF000000 == 0x33000000
            c = r.readformat('I')
        elif extra_type == 0x14:
            r.readformat('4I')
        elif extra_type == 0x15:
            a = r.readformat('I')
            b = r.readformat('I')
            c, d, e = r.readformat('3f')

            assert a == 0 or a == 1 or a == 0xffffffff
            assert b & 0xFF000000 == 0x0A000000
            # this does not look like x, y, z for 3D positioning of a sound
            # maybe volume, play speed and something else? or bass, midrange, treble?
            assert c >= 0.0 and c <= 1.0
            assert d >= 0.0 and d <= 3.0
            assert e >= 0.0 and e <= 6.0

        elif extra_type == 0x16:
            r.readformat('4I')
        else:
            raise RuntimeError('unknown extra_type: {:08x}'.format(extra_type))

assert len(r) == 0

