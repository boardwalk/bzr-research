#!/usr/bin/env python
import sys
import wave
from reader import Reader

r = Reader(sys.stdin.buffer.raw.read())
r.dump()

