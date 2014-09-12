#!/usr/bin/env python
import sys
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid == 0x0e00000e

def readcryptstring(r):
    numChars = r.readshort()
    if numChars == 0xFFFF:
        numChars = r.readint()
    chars = bytearray( r.readformat('{}s'.format(numChars)) )
    for i in range(len(chars)):
        chars[i] = ((chars[i] << 4) & 0xFF)| (chars[i] >> 4)
    r.align()
    return chars.decode('cp1252')

print('=== fid = {:08x}'.format(fid))

count = r.readshort()

unk1 = r.readshort()
assert unk1 == 0x2000

for i in range(count):
    iden = r.readint()
    name = readcryptstring(r)
    desc = readcryptstring(r)
    print('iden = {:08x} name = "{}" desc = "{}"'.format(iden, name, desc))

    # 1 war
    # 2 life
    # 3 item
    # 4 creature
    # 5 void
    school = r.readint()
    assert school in range(1, 6)

    # 0x06 file id
    icon = r.readint()
    assert icon & 0xFF000000 == 0x06000000
    
    # spells of the same basic function but different level or target
    # have the same family
    family = r.readint()

    flags = r.readint()
    assert flags & ~0x17CBF == 0

    #if flags & 1:
    #    print('  flag: offensive')
    #if flags & 2:
    #    print('  flag: unknown 2')
    #if flags & 4:
    #    print('  flag: irresistable')
    #if flags & 8:
    #    print('  flag: untargeted')
    #if flags & 0x10:
    #    print('  flag: debuff')
    #if flags & 0x20:
    #    print('  flag: rain-style spell')
    #if flags & 0x80:
    #    print('  flag: unresearchable')
    #if flags & 0x400:
    #    print('  flag: cantrip')
    #if flags & 0x800:
    #    print('  flag: unknown 800')
    #if flags & 0x1000:
    #    print('  flag: arc')
    #if flags & 0x2000:
    #    print('  flag: fellowship')
    #if flags & 0x4000:
    #    print('  flag: fast windup')
    #if flags & 0x10000:
    #    print('flag: damage over time')

    mana = r.readint()

    # I'm not what the actual meaning of these is
    range1 = r.readfloat()
    range2 = r.readfloat()

    difficulty = r.readint()

    # 0.0 = not effected by spell economy
    # 1.0 = effected by spell economy
    economy = r.readfloat()
    assert economy in [0.0, 1.0]

    # I don't know wtf this is
    generation = r.readint()
    assert generation in [0x1, 0x2, 0x3, 0xE]

    # larger is slower
    # not sure of units
    speed = r.readfloat()

    typ = r.readint()

    iden2 = r.readint()
    assert iden2 == iden

    if typ == 1 or typ == 7 or typ == 12:
        # duration in seconds
        dur = r.readformat('d')

    if typ == 1 or typ == 12:
        unk2 = r.readint()
        assert unk2 == 0
        unk3 = r.readint()
        assert unk3 == 0xc4268000

    for j in range(8): # components
        r.readint()

    # The visual effect ID
    # see Effect DWORD in protocol docs
    castereffect = r.readint()
    targeteffect = r.readint()

    for j in range(4): # unknown
        unk4 = r.readint()
        assert unk4 == 0

    sortOrder = r.readint()

    # see ObjectCategoryFlags DWORD in protocol docs
    # 0x00000001 weapon
    # 0x00000002 armor
    # 0x00000004 clothing
    # 0x00000010 creature
    # 0x00000080 misc
    # 0x00000100 missile weapon/ammo
    # 0x00010000 portal
    # 0x00000200 container
    targetMask = r.readint()

    # for spells that can effect multiple targets
    # e.g. fellowship-wide, banes
    perTargetMana = r.readint()

