#!/usr/bin/env python
import sys
from reader import Reader

def readcryptstring(r):
    numChars = r.readshort()
    if numChars == 0xFFFF:
        numChars = r.readint()
    chars = bytearray( r.readformat('{}s'.format(numChars)) )
    for i in range(len(chars)):
        chars[i] = ((chars[i] << 4) & 0xFF)| (chars[i] >> 4)
    r.align()
    return chars.decode('cp1252')

def readstring(r):
    numChars = r.readshort()
    if numChars == 0xFFFF:
        numChars = r.readint()
    chars = r.readformat('{}s'.format(numChars))
    r.align()
    return chars.decode('cp1252')

def readarray(r):
    numBytes = r.readshort()
    if numBytes == 0xFFFF:
        numBytes = r.readint()
    bytes = r.readformat('{}s'.format(numBytes))
    r.align()
    return bytes

r = Reader(sys.stdin.buffer.raw.read())

fid = r.readint()
assert fid & 0xFF000000 == 0x0E000000
print('=== fid = {:08x}'.format(fid))

if fid == 0x0e00000e: # spell table
    count = r.readshort()

    unk1 = r.readshort()
    assert unk1 == 0x2000

    for i in range(count):
        iden = r.readint()
        name = readcryptstring(r)
        desc = readcryptstring(r)
        #print('iden = {:08x} name = "{}" desc = "{}"'.format(iden, name, desc))

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

elif fid == 0x0e00000f: # components
    count = r.readshort()

    unk1 = r.readshort()
    assert unk1 == 0x100

    for i in range(count):
        iden = r.readint()
        name = readcryptstring(r)
        typ = r.readint()

        icon = r.readint()
        assert icon & 0xFF000000 == 0x06000000

        sort = r.readint()
        gestureId = r.readint()
        gestureSpeed = r.readfloat()
        word = readcryptstring(r)
        burnRate = r.readfloat()

elif fid == 0x0e00000d: # i don't know wtf this shit is
    sys.exit()
    count = r.readshort()
    unk1 = r.readshort()
    while len(r):
        unk2 = r.readint()
        iden = r.readint()
        name = readcryptstring(r)
        print('{:08x} {:08x} {}'.format(unk2, iden, name))

elif fid == 0x0e000004: # skills
    count = r.readshort()
    unk1 = r.readshort()
    for i in range(count):
        iden = r.readint()
        desc = readstring(r)
        name = readstring(r)
        
        icon = r.readint()
        assert icon & 0xFF000000 == 0x06000000
        
        trainCost = r.readint()
        specCost = r.readint()

        # 1 = melee (two handed, melee defense, summoning...)
        # 2 = utility (cooking, assess person...)
        # 3 = magic (life magic, mana conversion...)
        typ = r.readint()
        assert typ in [1, 2, 3]

        unk2 = r.readint()
        assert unk2 == 1

        usableUntrained = r.readint()
        
        unk3 = r.readint()
        assert unk3 == 0

        baseAttrib1Valid = r.readint()
        baseAttrib2Valid = r.readint()
        baseAttribDivisor = r.readint()
        baseAttrib1 = r.readint()
        baseAttrib2 = r.readint()

        xptimerLimit = r.readformat('d')
        xptimerStart = r.readformat('d')

        unk4 = r.readformat('d')
        assert unk4 == 1.0

        print('{:08x} name = "{}" desc = "{}"'.format(iden, name, desc))
        #print('  trainCost = {} specCost = {}'.format(trainCost, specCost))
        #print(' baseAttrib1 = {} baseAttrib2 = {} divisor = {}'.format(baseAttrib1, baseAttrib2, baseAttribDivisor))
        print('  typ = {}'.format(typ))
        print('  xptimerLimit = {:.2f} xptimerStart = {:.2f}'.format(xptimerLimit, xptimerStart))
        print('  usableUntrained = {}'.format(usableUntrained))

elif fid == 0x0e00001d:
    count = r.readshort()
    unk1 = r.readshort()
    for i in range(count):
        unk2 = r.readint() # 1
        unk3 = r.readint() # 0
        unk4 = r.readint() # 1
        name = readstring(r)
        desc = readstring(r)
        unk5 = r.readint() # 0
        targetName = readstring(r)
        unk6 = r.readint() # 0
        unk7 = r.readint() # 0
        name2 = readstring(r) # EmoteTestNPCQuest
        desc2 = readstring(r) # ShadowsWinterComplete1205
        unk8 = r.readint() # 0
        unk9 = r.readint() # 0
        targetName = readstring(r) # EmoteTestNPCQuest
        #readarray(r)
        #unk10 = r.readint() # 0
        #unk11 = r.readint() # 0
        #readarray(r)
        break

    r.dump(maxlen=512)

else:
    r.dump(maxlen=256)
