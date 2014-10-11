#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
anim_type = r.readint()
num_parts = r.readint()
num_frames = r.readint()

print('=== fid = {:08x}'.format(fid))

#if anim_type == 1 or anim_type == 3:
if anim_type & 1:
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
        extra_thing = r.readint()
        assert extra_thing == 0 or extra_thing == 1 or extra_thing == 0xFFFFFFFF
        if extra_type == 0x01:
            a = r.readformat('I')
            assert (a & 0xFF000000) == 0x0A000000
        elif extra_type == 0x02:
            a = r.readformat('I')
            assert a <= 0xFF
        elif extra_type == 0x03:
            r.readformat('7I')
        elif extra_type == 0x05:
            part_index = r.readformat('I')
            print('ReplaceObjectHook {:08x}'.format(part_index))
        elif extra_type == 0x06:
            r.readformat('I')
        elif extra_type == 0x07:
            r.readformat('4I')
        elif extra_type == 0x0D:
            r.readformat('10I')
        elif extra_type == 0x0F:
            r.readformat('I')
        elif extra_type == 0x11:
            pass
        elif extra_type == 0x13:
            a = r.readformat('I')
            assert a & 0xFF000000 == 0x33000000
            b = r.readformat('I')

        elif extra_type == 0x14:
            start, end, time = r.readformat('3f')
            #print('TransparentHook {:.2f} {:.2f} {:.2f}'.format(start, end, time))

        elif extra_type == 0x15:
            gid = r.readformat('I')
            priority, probability, volume = r.readformat('3f')
            assert gid & 0xFF000000 == 0x0A000000
            #print('SoundTweaked {:08x} {:.2f} {:.2f} {:.2f}'.format(gid, priority, probability, volume))

        elif extra_type == 0x16:
            x, y, z = r.readformat('3f')
            #print('SetOmega {:.1f} {:.2f} {:.2f}'.format(x, y, z))

        else:
            raise RuntimeError('unknown extra_type: {:08x}'.format(extra_type))

assert len(r) == 0

