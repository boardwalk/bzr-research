#!/usr/bin/env python
import struct
import subprocess
import sys

header = sys.stdin.buffer.raw.read(24)

fid, unk, w, h, fmt, data_size = struct.unpack('6I', header)

print('fid={:08x} w={} h={} fmt={:08x}'.format(fid, w, h, fmt))

if fmt == 0x14:
    channels = 'bgr'
elif fmt == 0x15:
    channels = 'bgra'
elif fmt == 0xf3:
    channels = 'rgb'
elif fmt == 0xf4:
    channels = 'a'
else:
    sys.stdin.buffer.raw.readall()
    sys.exit()

args = ['convert',
    '-size', '{}x{}'.format(w, h),
    '-depth', '8',
    '{}:-'.format(channels),
    'output/{:08x}.png'.format(fid)]

subprocess.check_call(args, stdin=sys.stdin.buffer.raw)

