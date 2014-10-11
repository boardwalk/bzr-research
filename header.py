
# "ProtoHeader"
class Header(object):
    def __init__(self, r):
        self.sequence = r.readint() # "seqID"
        self.flags = r.readint() # "header"
        self.checksum = r.readint() # "checksum"
        self.netid = r.readshort() # "recID"
        self.time = r.readshort() # "interval"
        self.size = r.readshort() # "datalen"
        self.session = r.readshort() # "iteration"
        assert self.size == len(r)

    def __str__(self):
        return 'Header(sequence={sequence:08x} flags={flags:08x} checksum={checksum:08x} ' \
            'netid={netid:04x} time={time:04x} size={size:04x} session={session:04x})'.format(**self.__dict__)

class FragmentHeader(object):
    def __init__(self, r):
        self.blobId = r.readformat('Q')
        self.fragmentCount = r.readshort()
        self.fragmentLength = r.readshort()
        self.fragmentIndex = r.readshort()
        self.queueId = r.readshort()
        assert self.fragmentIndex < self.fragmentCount
    def __str__(self):
        return 'FragmentHeader(blobId={blobId:016x} count={fragmentCount:04x} len={fragmentLength:04x} index={fragmentIndex:04x} ' \
            'queueId={queueId:04x})'.format(**self.__dict__)

