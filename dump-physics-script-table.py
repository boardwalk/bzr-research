#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x34000000

print('=== fid {:08x}'.format(fid))

numTableData = r.readint()

for i in range(numTableData):
    key = r.readint()
    numInner = r.readint()
    for j in range(numInner):
        mod = r.readfloat()
        physicsScript = r.readint()
        assert physicsScript & 0xFF000000 == 0x33000000

assert len(r) == 0

