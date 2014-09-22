import ipaddress
import codecs
from header import Header

def readstring(r):
    size = r.readshort()
    s = r.readformat('{}s'.format(size))
    r.align()
    return s

class Session(object):
    def __init__(self, name):
        self.name = name
        self.source = '------'
        self.client_endpoint = 0
        self.server_endpoint = 0
        self.begin_time = 0.0
        self.last_ping = 0.0
        self.log('new session')

    def log(self, fmt, *args, **kwargs):
        print('{} {} {}'.format(self.name, self.source, fmt.format(*args, **kwargs)))

    def handle_client_pkt(self, r):
        self.source = 'client'
        hdr = Header(r)
        assert hdr.endpoint == self.client_endpoint
        self.handle_pkt_major(hdr, r)

    def handle_server_pkt(self, r):
        self.source = 'server'
        hdr = Header(r)
        if hdr.endpoint != 0:
            self.server_endpoint = hdr.endpoint
        assert hdr.endpoint == self.server_endpoint
        self.handle_pkt_major(hdr, r)
   
    def handle_pkt_major(self, hdr, r):
        self.log('{}'.format(hdr))
        if hdr.flags == 0x00010000:
            self.handle_client_login_hello(hdr, r)
        elif hdr.flags == 0x00020000:
            self.handle_client_world_hello(hdr, r)
        elif hdr.flags == 0x00040000:
            self.handle_server_hello(hdr, r)
        elif hdr.flags == 0x00080000:
            self.handle_client_hello_reply(hdr, r)
        else:
            self.handle_pkt(hdr, r)

        assert len(r) == 0

    def handle_client_login_hello(self, hdr, r):
        self.log('client login hello')

        assert hdr.sequence == 0
        # TODO crc
        assert hdr.endpoint == 0
        assert hdr.unk2 == 0
        assert hdr.session == 0

        version = readstring(r)
        unk3 = r.readshort()
        unk4 = r.readshort()
        unk5 = r.readshort()
        unk6 = r.readshort()
        unk7 = r.readshort()
        unk8 = r.readshort()
        unixtime = r.readint()
        accountname = readstring(r)
        unk9 = r.readint()
        accountkeylen = r.readint()
        accountkey = r.readformat('{}s'.format(accountkeylen))

        assert version == b'1802' # NetVersion
        assert unk3 == 0x0126
        assert unk4 == 0
        assert unk5 == 2
        assert unk6 == 0x4000
        assert unk7 == 0
        assert unk8 == 0
        assert unk9 == 0
        assert accountkeylen == 246

    def handle_client_world_hello(self, hdr, r):
        token = r.readformat('8s')
        self.log('client world hello with token {}', codecs.encode(token, 'hex'))

    def handle_server_hello(self, hdr, r):
        # appears to be "seconds since Asheron's Call epoch"
        # where the epoch is approximately 1995-09-27 06:00 UTC
        self.begin_time = r.readformat('d')
        # the value the client should use in client_hello_reply
        token = r.readformat('8s')
        # the value the client should use for the endpoint header field
        self.client_endpoint = r.readformat('H')
        unk2 = r.readformat('14s')
        self.log('server hello with token {}, unk2 {}', codecs.encode(token, 'hex'),
            codecs.encode(unk2, 'hex'))

    def handle_client_hello_reply(self, hdr, r):
        token = r.readformat('8s')
        self.log('client hello reply with token {}', codecs.encode(token, 'hex'))

    def handle_pkt(self, hdr, r):
        if hdr.flags & 0x00000002:
            #self.log('  [00000002] connected')
            hdr.flags &= ~0x00000002

        if hdr.flags & 0x00000100:
            unk0 = r.readformat('8s')
            self.log('  [00000100] {}', codecs.encode(unk0, 'hex'))
            hdr.flags &= ~0x00000100

        if hdr.flags == 0x00000800:
            token, family, port, addr, zero, unk6 = r.readformat('!8sHHI8s8s')
            self.log('server transfer {}:{} with token {}', ipaddress.ip_address(addr), port, codecs.encode(token, 'hex'))
            hdr.flags &= ~0x00000800

        if hdr.flags & 0x00004000:
            sequence = r.readint()
            self.log('  [00004000] ack sequence {:x}', sequence)
            hdr.flags &= ~0x00004000

        if hdr.flags & 0x00008000:
            self.log('  [00008000] disconnect')
            hdr.flags &= ~0x00008000

        if hdr.flags & 0x00400000:
            unk5 = r.readformat('8s')
            self.log('  [00400000] {}', codecs.encode(unk5, 'hex'))
            hdr.flags &= ~0x00400000

        if hdr.flags & 0x01000000:
            time = r.readformat('d')
            self.log('  [01000000] time {}', time)
            hdr.flags &= ~0x01000000
            assert time >= self.begin_time and time <= self.begin_time + 3600.0

        if hdr.flags & 0x02000000:
            self.last_ping = r.readformat('f')
            self.log('  [02000000] ping {:.2f}', self.last_ping)
            hdr.flags &= ~0x02000000

        if hdr.flags & 0x04000000:
            ping_time = r.readformat('f')
            ping_result = r.readformat('f') # a delta maybe?
            self.log('  [04000000] pong {:.2f} {:.2f}', ping_time, ping_result)
            hdr.flags &= ~0x04000000
            assert ping_time == self.last_ping

        if hdr.flags & 0x08000000:
            unk4 = r.readformat('6s')
            self.log('  [08000000] {}', codecs.encode(unk4, 'hex'))
            hdr.flags &= ~0x08000000

        if hdr.flags & 0x00000004:
            while len(r):
                senderId = r.readint()
                receiverId = r.readint()
                fragmentCount = r.readshort()
                fragmentLength = r.readshort()
                fragmentIndex = r.readshort()
                unk4 = r.readshort()
                self.log('  [00000004] fragment {:08x}, {:08x}, {:04x}, {:04x}, {:04x}, {:04}'.format(
                    senderId, receiverId, fragmentCount, fragmentLength, fragmentIndex, unk4))
                if fragmentIndex == 0:
                    messageType = r.readint()
                    r.skip(fragmentLength - 20)
                    self.log('  [00000004] message {:08x}'.format(messageType))
                else:
                    r.skip(fragmentLength - 16)
            hdr.flags &= ~0x00000004

        if hdr.flags != 0:
            #r.dump()
            raise RuntimeError('Unknown flags: {:08x}'.format(hdr.flags))

