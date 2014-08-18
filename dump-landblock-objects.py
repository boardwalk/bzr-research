#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())
#r.dump(1024)

fid = r.readint()
assert fid & 0x0000FFFF == 0x0000FFFE

unk = r.readint()

numObjects = r.readint()

for i in range(numObjects):
    modelId = r.readint()
    x, y, z = r.readformat('3f')
    assert x >= 0.0 and x <= 192.0
    assert y >= 0.0 and y <= 192.0
    assert z >= 0.0 and z <= 512.0
    rw, rx, ry, rz = r.readformat('4f')

numObjectsEx = r.readint()

print("working on {:08x}, numobjectsex={}".format(fid, numObjectsEx))

r.dump(2048)

for i in range(numObjectsEx):
    modelId = r.readint()
    print("{}, {:08x}".format(i, modelId))
    #if i == 1:
    #    r.dump(1024)
    assert modelId & 0xFFFF0000 == 0x01000000
    x, y, z = r.readformat('3f')
    assert x >= 0.0 and x <= 192.0
    assert y >= 0.0 and y <= 192.0
    assert z >= 0.0 and z <= 192.0
    rw, rx, ry, rz = r.readformat('4f')
    assert rw >= -1.0 and rw <= 1.0
    assert rx >= -1.0 and rx <= 1.0
    assert ry >= -1.0 and ry <= 1.0
    assert rz >= -1.0 and rz <= 1.0
    unks = r.readformat('4B')
    #if unks[0] == 216:
    #    bytesperchunk = 4 * 4
    #elif unks[0] == 235:
    #    bytesperchunk = 5 * 4
    #elif unks[0] == 32:
    #    bytesperchunk = 7 * 4
    #elif unks[0] == 127:
    #    bytesperchunk = 12 * 4
    #else:
    #    bytesperchunk = 3 * 4
    #assert unks[2] == 0
    #assert unks[3] == 0
    numChunks = r.readint()
    print("reading {} chunks".format(numChunks))
    #r.readraw(numChunks * bytesperchunk)

    for j in range(numChunks):
        print("chunk {}".format(j))
        three = r.readshort()
        #print("three: {}".format(three))
        assert three == 3 or three == 2
        r.readshort()
        r.readshort()
        r.readshort()
        while r.readshort() != 0:
            print(" ...")
            pass

    #print("numchunks {}, bytesperchunk {}, unks {}, {}, {}, {}".format(numchunks, bytesperchunk, *unks))

#print("numObjectsEx: {}".format(numObjectsEx))


