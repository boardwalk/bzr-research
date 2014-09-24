from ctypes import *

__all__ = ['ChecksumXorGenerator']

lib = cdll.LoadLibrary('./ChecksumXorGenerator.so')

# c_void_p *does not work*
# it seems to sign extend my pointers!
handle_type = POINTER(c_char)

create = lib.generator_create
create.arg_types = [c_uint]
create.restype = handle_type

generate = lib.generator_generate
generate.arg_types = [handle_type]
generate.restype = c_uint

destroy = lib.generator_destroy
destroy.arg_types = [handle_type]
destroy.restype = None

class ChecksumXorGenerator(object):
    def __init__(self, seed):
        self.handle = create(seed)
        # dummy values, there is no sequence 0 or 1
        self.cached = [0xDEADBEEF, 0xDEADBEEF]

    def __call__(self, sequence):
        while sequence >= len(self.cached):
            self.cached.append(generate(self.handle))
        return self.cached[sequence]

    def __del__(self):
        # destroy *may* get deleted before we do
        if destroy is not None:
            destroy(self.handle)
