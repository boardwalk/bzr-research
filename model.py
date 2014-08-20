import math

__all__ = ['unpack_trifan', 'unpack_vertex']

def unpack_trifan(r, i):
    primnum = r.readshort()
    assert primnum == i

    numindices = r.readbyte()
    primflags = r.readbyte()
    assert primflags in [0x00, 0x01, 0x04]
    primflags2 = r.readint()
    assert primflags2 in [0x00, 0x01, 0x02]
    texIndex = r.readshort()
    r.readshort()

    for i in range(numindices):
        vertindex = r.readshort()

    if primflags != 0x04:
        for i in range(numindices):
            texCoordIndex = r.readbyte()

    if primflags2 == 0x02:
        for i in range(numindices):
            r.readbyte()

def unpack_vertex(r, i):
    vertexnum = r.readshort()
    assert vertexnum == i

    ntexcoord = r.readshort()

    vx, vy, vz = r.readformat('3f')

    assert abs(vx) < 15000.0 and abs(vy) < 15000.0 and abs(vz) < 15000.0

    nx, ny, nz = r.readformat('3f')
    mag_n = math.sqrt(nx * nx + ny * ny + nz * nz)
    assert (mag_n >= 0.99 and mag_n <= 1.01) or mag_n == 0.0

    for j in range(ntexcoord):
        s, t = r.readformat('2f')
