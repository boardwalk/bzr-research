#!/usr/bin/env python
import sys
import wave
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x0A000000

typ = r.readint()
dataLen = r.readint()
unk2 = r.readshort()
unk3 = r.readshort()

channelSampleRate = r.readint()
totalSampleRate = r.readint()
numChannels = r.readshort()
bitsPerSample = r.readint()

print('==== fid = {:08x}'.format(fid))

if typ == 18:
    print('unk2 = {} unk3 = {} channelSampleRate = {} totalSampleRate = {} numChannels = {} bitsPerSample = {}'
            .format(unk2, unk3, channelSampleRate, totalSampleRate, numChannels, bitsPerSample))
    assert typ == 18
    assert dataLen == len(r)
    assert unk2 == 1
    assert unk3 == 1 or unk3 == 2
    assert bitsPerSample == 8 or bitsPerSample == 16
    assert channelSampleRate * numChannels == totalSampleRate
    assert numChannels == 1 or numChannels == 2 or numChannels == 4

    #duration = float(dataLen) / float(bitsPerSample / 8 * totalSampleRate)
    #print('duration = {:.2f}'.format(duration))

    wav = wave.open('0a/{:08x}.wav'.format(fid), 'w')
    wav.setparams((numChannels, bitsPerSample // 8, channelSampleRate // 2, 0, 'NONE', 'no compression'))
    wav.writeframes(r.raw())
else:
    print('unknown typ = {}'.format(typ))

#r.dump()
