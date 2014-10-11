#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x22000000
print('=== fid = {:08x}'.format(fid))

base_mapper = r.readint()
assert base_mapper == 0 or base_mapper & 0xFF000000 == 0x22000000

unk = r.readbyte()
assert unk <= 7

numPairs = r.readvarint()

def readstring(s):
    size = r.readvarint()
    s = r.readformat('{}s'.format(size))
    #r.align()
    return s.decode('cp1252')

for i in range(numPairs):
    key = r.readint()
    value = readstring(r)

assert len(r) == 0
#r.dump(maxlen=256)

