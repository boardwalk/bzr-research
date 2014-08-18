#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

r.dump()

image_id, zero, two, num_palettes = r.readformat('=IIBI')
palettes = [r.readint() for i in range(num_palettes)]

print("{:08x} {} {} {}".format(image_id, zero, two, num_palettes))

print( ' '.join(['{:08x}'.format(p) for p in palettes]) )
#print(palettes)

assert zero == 0
assert two == 2
assert len(r) == 0

#r.dump(1024)

#print("-----")

