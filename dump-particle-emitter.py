#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x32000000
print('=== fid = {:08x}'.format(fid))

unk = r.readint()
assert unk == 0

emitter_type = r.readint()
assert emitter_type >= 0x1 and emitter_type <= 0x2

particle_type = r.readint()
assert particle_type >= 0x1 and particle_type <= 0xc

print('unk = {:08x} emitter_type = {:08x} particle_type = {:08x}'.format(unk, emitter_type, particle_type))

gfxobj_id = r.readint()
print('gfxobj_id = {:08x}'.format(gfxobj_id))
assert gfxobj_id == 0 or (gfxobj_id & 0xFF000000) == 0x01000000

hw_gfxobj_id = r.readint()
print('hw_gfxobj_id = {:08x}'.format(hw_gfxobj_id))
assert hw_gfxobj_id == 0 or (hw_gfxobj_id & 0xFF000000) == 0x01000000

birthrate = r.readformat('d')
print('birthrate = {:.8f}'.format(birthrate))

max_particles = r.readint()
initial_particles = r.readint()
total_particles = r.readint()
print('max_particles = {}, initial_particles = {}, total_particles = {}'.format(max_particles, initial_particles, total_particles))

#r.readint() # pad

total_seconds = r.readformat('d')
lifespan_rand = r.readformat('d')
lifespan = r.readformat('d')
print('total_seconds = {:.2f} lifespan_rand = {:.2f} lifespan = {:.2f}'.format(total_seconds, lifespan_rand, lifespan))

# sorting sphere
#sx, sy, sz, sr = r.readformat('ffff')
sx, sy, sz, sr = 0.0, 0.0, 0.0, r.readformat('f')
print('sorting sphere = {:.2f} {:.2f} {:.2f} {:.2f}'.format(sx, sy, sz, sr))

# offset_dir
x, y, z = r.readformat('fff')
print('offset_dir = {:.2f} {:.2f} {:.2f}'.format(x, y, z))

min_offset = r.readfloat()
max_offset = r.readfloat()
print('min_offset = {:.2f} max_offset = {:.2f}'.format(min_offset, max_offset))

ax, ay, az = r.readformat('fff')
print('a = {:.2f} {:.2f} {:.2f}'.format(ax, ay, az))

bx, by, bz = r.readformat('fff')
print('b = {:.2f} {:.2f} {:.2f}'.format(bx, by, bz))

cx, cy, cz = r.readformat('fff')
print('c = {:.2f} {:.2f} {:.2f}'.format(cx, cy, cz))

min_a, max_a = r.readformat('ff')
min_b, max_b = r.readformat('ff')
min_c, max_c = r.readformat('ff')

print('a range = [{:.2f}, {:.2f}]'.format(min_a, max_a))
print('b range = [{:.2f}, {:.2f}]'.format(min_b, max_b))
print('c range = [{:.2f}, {:.2f}]'.format(min_c, max_c))

#assert min_a <= max_a
#assert min_b <= max_b
#assert min_c <= max_c

scale_rand, start_scale, final_scale = r.readformat('fff')
print('scale_rand = {:.2f} start_scale = {:.2f} final_scale = {:.2f}'.format(scale_rand, start_scale, final_scale))

trans_rand, start_trans, final_trans = r.readformat('fff')
print('trans_rand = {:.2f} start_trans = {:.2f} final_trans = {:.2f}'.format(trans_rand, start_trans, final_trans))

r.dump(maxlen=256)

assert len(r) == 0

