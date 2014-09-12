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

for i in range(count):
    iden = r.readint()
    name = readcryptstring(r)
    desc = readcryptstring(r)
    print('iden = {:08x}, name = "{}" desc = "{}"'.format(iden, name, desc))

    # family
    # 1 war
    # 2 life
    # 3 item
    # 4 creature
    # 5 void
    family = r.readint() # GOOD!
    assert family in range(1, 6)

    # 0x06 file id
    icon = r.readint() # GOOD!
    assert icon & 0xFF000000 == 0x06000000
    
    # some sort of effect id perhaps?
    unk = r.readint()
    print('  unk = {}'.format(unk))

    flags = r.readint()
    assert flags & ~0x17CBF == 0 # GOOD!

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

    mana = r.readint() # GOOD!

    range1 = r.readfloat()

    difficulty = r.readfloat()
    print('  range1: {:.2f} {:.2f}'.format(range1, difficulty))

    economy = r.readint()
    #print('  range1 = {:.2f} range2 = {:.2f} difficulty = {:.2f} economy = {:08x}'.format(range1, range2, difficulty, economy))

    generation, unk2, speed, typ, iden2 = r.readformat('fIIII')
    #print('  generation = {:.2f} unk2 = {:08x} speed = {:08x} type = {:08x} iden2 = {:08x}'.format(generation, unk2, speed, typ, iden2))

    if typ == 1 or typ == 7 or typ == 12:
        bar = r.readint()
        dur1 = r.readformat('f')
        #duration = r.readformat('d')
        #print(' duration = {:.2f}'.format(duration))

    if typ == 1 or typ == 12:
        baz = r.readint()
        dur2 = r.readformat('f')


    for j in range(8): # components
        r.readint()

    castereffect = r.readint()
    targeteffect = r.readint()

    for j in range(4): # unknown
        r.readint()

    sortOrder = r.readint()
    targetMask = r.readint()
    fellowship = r.readint()
    #print('  castereffect = {:08x} targeteffect = {:08x} sortOrder = {:08x} targetMask = {:08x} fellowship = {:08x}'.format(castereffect, targeteffect, sortOrder, targetMask, fellowship))

