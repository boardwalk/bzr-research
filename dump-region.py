#!/usr/bin/env python
import sys
from reader import Reader

def readstring(r):
    size = r.readshort()
    s = r.readformat('{}s'.format(size))
    r.align()
    return s.decode('cp1252')

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x13000000
print('=== fid = {:08x}'.format(fid))

version = r.readint()
assert version == 1

region_number = r.readint()
assert region_number == 3

region_name = readstring(r)
assert region_name == 'Dereth'

unk1 = r.readint()
assert unk1 == 0xFF

unk2 = r.readint()
assert unk2 == 0xFF

r.dump(2048, perline=32)

r.skip(6 * 4)

for i in range(256):
    h = r.readfloat()
    print('{} {}'.format(i, h))

r.skip(7 * 4)

nhours = r.readint()

for hournum in range(nhours):
    start_time = r.readfloat()
    night_time = r.readint()
    hour_name = readstring(r)
    print('start_time = {} hour_name = {} night_time = {}'.format(start_time, hour_name, night_time))

nholidays = r.readint()

for holidaynum in range(nholidays):
    holiday_name = readstring(r)
    print('holiday_name = {}'.format(holiday_name))

nseasons = r.readint()

for seasonnum in range(nseasons):
    start_day = r.readint()
    season_name = readstring(r)
    print('start_day = {} season_name = {}'.format(start_day, season_name))

r.dump(maxlen=49400)
r.skip(49400)

nscenetype = r.readint()
assert nscenetype == 0x59

for i in range(nscenetype):
    scenetypeunk = r.readint()
    scenecount = r.readint()
    print('scenetypeunk = {:08x}, scenecount = {}'.format(scenetypeunk, scenecount))
    for i in range(scenecount):
        sceneid = r.readint()
        assert sceneid & 0xFF000000 == 0x12000000

nterrain = r.readint()
assert nterrain == 0x20

for terrainnum in range(nterrain):
    terrain_name = readstring(r)
    terrain_color = r.readint()
    terrain_nunk2 = r.readint()
    print('terrain_name = {} terrain_color = {:08x} terrain_nunk2 = {}'.format(terrain_name, terrain_color, terrain_nunk2))
    for i in range(terrain_nunk2):
        scenetype_num = r.readint()
        print('  scenetype_num = {:08x}'.format(scenetype_num))
        assert scenetype_num < nscenetype

unk3 = r.readint()
assert unk3 == 0

unk4 = r.readint()
assert unk4 == 0x400

def tcode_name(tcode):
    if tcode == 8:
        return "corner"
    if tcode == 9:
        return "edge"
    if tcode == 10:
        return "diagonal"
    assert False

def parse_blend_tex():
    nblendtex = r.readint()
    for i in range(nblendtex):
        tcode = r.readint()
        blend_tex_id = r.readint()
        print('{} {} blend_tex_id = {:08x}'.format(i, tcode_name(tcode), blend_tex_id))

parse_blend_tex()
parse_blend_tex()
parse_blend_tex()

nterraintex = r.readint()
assert nterraintex == 0x21

for i in range(nterraintex):
    idx = r.readint()
    assert idx == i
    tex_id = r.readint()
    tex_tiling = r.readint()
    max_vert_bright, min_vert_bright = r.readformat('2I')
    assert max_vert_bright >= min_vert_bright
    max_vert_saturate, min_vert_saturate = r.readformat('2I')
    assert max_vert_saturate >= min_vert_saturate
    max_vert_hue, min_vert_hue = r.readformat('2I')
    assert max_vert_hue >= min_vert_hue
    detail_tex_tiling = r.readint()
    detail_tex_id = r.readint()
    print('tex_id = {:08x} detail_tex_id = {:08x}'.format(tex_id, detail_tex_id))

unk5 = r.readint()
assert unk5 == 1

r.readint() # small map
r.readint() # large map

r.dump()

#assert len(r) == 0

