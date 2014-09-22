
class Header(object):
    def __init__(self, r):
        self.sequence = r.readint()
        self.flags = r.readint()
        self.crc = r.readint()
        self.endpoint = r.readshort()
        self.time = r.readshort()
        self.size = r.readshort()
        self.session = r.readshort()
        assert self.size == len(r)

    def __str__(self):
        return 'Header(sequence={sequence:08x} flags={flags:08x} crc={crc:08x} ' \
            'endpoint={endpoint:04x} time={time:04x} size={size:04x} session={session:04x})'.format(**self.__dict__)

