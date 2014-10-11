#!/usr/bin/env python
import sys
import wave
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())
#r.dump()
fid = r.readint()
assert fid & 0xFF000000 == 0x20000000

unk1 = r.readint()
assert unk1 == 0

unk2 = r.readint()
assert unk2 == 1

unk3 = r.readint()
assert unk3 == 0

unk4 = r.readint()
assert unk4 == 0

unk5 = r.readfloat()
assert unk5 == 1.0

unk6 = r.readfloat()
assert unk6 == 1.0

numcount1 = r.readint()

print('fid = {:08x}'.format(fid))

for i in range(numcount1):
    sound_type = r.readformat('I')
    numcount2 = r.readformat('I')
    for j in range(numcount2):
        sound_gid = r.readformat('I')
        assert (sound_gid & 0xFF000000) == 0x0A000000
        priority = r.readformat('f')
        assert priority >= 0.0 and priority <= 1.0
        probability = r.readformat('f')
        assert probability >= 0.0 and priority <= 1.0
        volume = r.readformat('f')
        assert volume >= 0.0 and priority <= 1.0
        #print('{} {} sound_gid = {:08x} priority = {:.2f} probability = {:.2f} volume = {:.2f}'
        #        .format(i, j, sound_gid, priority, probability, volume))

    unk2 = r.readformat('I')
    assert unk2 == 0

assert len(r) == 0

