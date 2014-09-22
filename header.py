
class Header(object):
    def __init__(self, r):
        # starts at 2 and increments for each message
        self.sequence = r.readint()
        self.flags = r.readint()
        self.crc = r.readint()
        # appears to be an endpoint identifier
        self.unk1 = r.readshort()
        # appears to be time in half-second units
        self.unk2 = r.readshort()
        # size in bytes excluding header
        self.size = r.readshort()
        self.session = r.readshort()
        assert self.size == len(r)

    def __str__(self):
        return 'Header(sequence={sequence:08x} flags={flags:08x} crc={crc:08x} ' \
            'unk1={unk1:04x} unk2={unk2:04x} size={size:04x} session={session:04x})'.format(**self.__dict__)

