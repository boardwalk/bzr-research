#!/usr/bin/env python
import sys
from reader import Reader

def read_object_desc(r):
    resource_id = r.readint()

    px, py, pz = r.readformat('3f')
    rw, rx, ry, rz = r.readformat('4f')
    freq = r.readformat('f')
    displace_x, displace_y = r.readformat('2f')
    assert(displace_x >= -24.0 and displace_x <= 24.0)
    assert(displace_y >= -24.0 and displace_y <= 24.0)
    #print("displace: {:.2f} {:.2f}".format(displace_x, displace_y))

    min_scale, max_scale = r.readformat('2f')
    max_rot = r.readformat('f')
    min_slope, max_slope = r.readformat('2f')
    align, orient, weenie_obj = r.readformat('3I')

    print('resource_id = {:08x}'.format(resource_id))
    #print('  p = {} {} {}'.format(px, py, pz))
    #print('  r = {} {} {} {}'.format(rw, rx, ry, rz))
    #print('  freq = {}'.format(freq))
    #print('  displace_x displace_y = {} {}'.format(displace_x, displace_y))
    #print('  min_scale max_scale = {} {}'.format(min_scale, max_scale))
    #print('  max_rot = {}'.format(max_rot))
    print('  min_slope, max_slope = {} {}'.format(min_slope, max_slope))
    #print('  align = {} orient = {} weenie_obj = {}'.format(align, orient, weenie_obj))

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x12000000
print('=== fid = {:08x}'.format(fid))

num_objects = r.readint()

for i in range(num_objects):
    read_object_desc(r)

assert len(r) == 0

