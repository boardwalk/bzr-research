#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())
#r.dump(1024)

flags = r.readint()

print("{} {:08x}".format(sys.argv[1], flags))

if flags & 0x01:
    thingie = r.readint()
    #print('thingie = {:08x}'.format(thingie))

if flags & 0x02 or flags & 0x04:
    textureId = r.readint()
    zero = r.readint()
    assert zero == 0
    #print('textureId = {:08x}'.format(textureId))

s, t, p = r.readformat('fff')

if flags & 0x10:
    assert s != 0.0
else:
    assert s == 0.0

assert len(r) == 0

#print('floats = {}, {}, {}'.format(s, t, p))

#
# 00000001 [thing including FF]           00000000  [a float] [a float]
# 00000002 [texture id]         00000000  00000000  [a float] [a float]
# 00000004 [texture id]         00000000  00000000  [a float] [a float]

# 00000011 [thing including FF]           [a float] [a float] [a float]
# 00000012 [texture id]         00000000  [a float] [a float] [a float]
# 00000014 [texture id]         00000000  [a float] [a float] [a float]
#

# ... & 1    has thing
# ... & 2    has texture id, 00000000
# ... & 4    has texture id, 00000000
# ... & 10   first float not zero

