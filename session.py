import ipaddress
import codecs
import struct
import sys
from header import Header
from checksumxorgenerator import ChecksumXorGenerator

messagenames = {}

with open('messagenames.csv') as f:
    for ln in f:
        t, n = ln.strip().split(',')
        messagenames[int(t, 16)] = n

def bswapword(w):
    return (w << 8) & 0xFF00 | (w >> 8)

def bswapdword(d):
    return (d << 24) & 0xFF000000 | (d << 8) & 0x00FF0000 | (d >> 8) & 0x0000FF00 | (d >> 24) & 0x000000FF

def readstring(r):
    size = r.readshort()
    s = r.readformat('{}s'.format(size))
    r.align()
    return s

def checksumdata(data, includesize):
    checksum = 0

    if includesize:
        checksum = (checksum + (len(data) << 16)) & 0xFFFFFFFF

    for i in range(0, len(data) & ~3, 4):
        checksum = (checksum + struct.unpack('I', data[i : i + 4])[0]) & 0xFFFFFFFF

    shift = 24
    for i in range(len(data) & ~3, len(data)):
        checksum = (checksum + (data[i] << shift)) & 0xFFFFFFFF
        shift -= 8

    return checksum

def checksumheader(data):
    header = data[: 20]
    header[8:12] = b'\xDD\x70\xDD\xBA'
    return checksumdata(header, True)

class Statistics(object):
    def __init__(self):
        self.messageinfos = {}

    def log(self, messagetype, source, flags):
        try:
            messageinfo = self.messageinfos[messagetype]
        except KeyError:
            messageinfo = {
                'sources': set(),
                'flags': set(),
                'count': 0
            }
            self.messageinfos[messagetype] = messageinfo
        messageinfo['sources'].add(source)
        messageinfo['flags'].add(flags)
        messageinfo['count'] += 1

    def __del__(self):
        for messagetype, messageinfo in self.messageinfos.items():
            print('{:08x}: {} {} {} {}'.format(messagetype, messagenames.get(messagetype, 'Unknown'), messageinfo['sources'], messageinfo['flags'], messageinfo['count']))

stats = Statistics()

CLIENT_COLOR = b'\x1b[31;1m'
SERVER_COLOR = b'\x1b[32;1m'
RESET_COLOR = b'\x1b[0m'

class Session(object):
    def __init__(self, name, time):
        self.name = name
        self.pkt_source = '------'
        self.pkt_time = None
        self.session_time = time
        self.begin_time = 0.0
        self.last_ping = 0.0
        self.server_bytes = 0
        self.client_bytes = 0
        self.calc_server_bytes = 0
        self.calc_client_bytes = 0
        self.log('new session')

    def log(self, fmt, *args, **kwargs):
        sys.stdout.buffer.write(SERVER_COLOR if self.pkt_source == 'server' else CLIENT_COLOR)
        sys.stdout.buffer.write('{} {} {}\n'.format(self.name, self.pkt_source, fmt.format(*args, **kwargs)).encode('utf-8'))
        sys.stdout.buffer.write(RESET_COLOR)

    def handle_pkt_major(self, r):

        pkt_data = r.raw()

        hdr = Header(r)
        self.log('{}'.format(hdr))

        if hdr.flags & 0x2:
            if self.pkt_source == 'server':
                self.calc_server_bytes += len(pkt_data)
            else:
                self.calc_client_bytes += len(pkt_data)

        if hdr.flags & 0x00000002:
            xor_generator = self.server_xor_generator if self.pkt_source == 'server' else self.client_xor_generator
            xor_val = xor_generator(hdr.sequence)
        else:
            xor_val = 0

        calc_checksum = checksumheader(pkt_data) + (checksumdata(pkt_data[20:], True) ^ xor_val) & 0xFFFFFFFF
        if calc_checksum != hdr.checksum:
            self.log('======= FAIL ====== {:08x}', calc_checksum)

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
        assert hdr.endpoint == 0
        assert hdr.time == 0
        assert hdr.session == 0

        version = readstring(r)
        unk3 = r.readshort()
        unk4 = r.readshort()
        unk5 = r.readint()
        unk6 = r.readshort()
        unk7 = r.readshort()
        unixtime = r.readint()
        accountname = readstring(r)
        unk9 = r.readint()
        accountkeylen = r.readint()
        accountkey = r.readformat('{}s'.format(accountkeylen))

        assert version == b'1802' # NetVersion
        assert unk3 == 0x0126
        assert unk4 == 0
        assert unk5 == 0x40000002 # GLSUserNameTicket_NetAuthType
        assert unk7 == 0
        assert unk9 == 0
        assert accountkeylen == 246

    def handle_client_world_hello(self, hdr, r):
        token = r.readformat('8s')
        self.log('client world hello with token {}', codecs.encode(token, 'hex'))

    def handle_server_hello(self, hdr, r):
        self.server_endpoint = hdr.endpoint
        self.session = hdr.session

        # appears to be "seconds since Asheron's Call epoch"
        # where the epoch is approximately 1995-09-27 06:00 UTC
        self.begin_time = r.readformat('d')

        # the value the client should use in client_hello_reply
        token = r.readformat('8s')

        # the value the client should use for the endpoint header field
        self.client_endpoint = r.readformat('H')

        # might just be padding for the previous
        r.readformat('H')

        serverseed = r.readint()
        clientseed = r.readint()

        self.server_xor_generator = ChecksumXorGenerator(serverseed)
        self.client_xor_generator = ChecksumXorGenerator(clientseed)

        # almost always zero
        unk = r.readint()

        self.log('server hello with token {}, server seed {:08x}, client seed {:08x}',
            codecs.encode(token, 'hex'), serverseed, clientseed)

    def handle_client_hello_reply(self, hdr, r):
        token = r.readformat('8s')
        self.log('client hello reply with token {}', codecs.encode(token, 'hex'))

    def handle_pkt(self, hdr, r):
        #assert hdr.session == self.session

        #if self.pkt_source == 'client':
        #    assert hdr.endpoint == self.client_endpoint
        #else:
        #    assert hdr.endpoint == self.server_endpoint

        if not hdr.flags & 0x00008000:
            # disconnect has hdr.time set to 0
            #assert abs((hdr.time / 2.0) - (self.pkt_time - self.session_time)) < 2.0
            pass

        if hdr.flags & 0x000000001:
            self.log('  [00000001] retransmission')
            hdr.flags &= ~0x00000001

        if hdr.flags & 0x00000002:
            self.log('  [00000002] encrypted checksum')
            hdr.flags &= ~0x00000002

        if hdr.flags & 0x00000100:
            unk0 = r.readformat('8s')
            self.log('  [00000100] {}', codecs.encode(unk0, 'hex'))
            hdr.flags &= ~0x00000100

        if hdr.flags == 0x00000800:
            token, family, port, addr, zero, unk6 = r.readformat('8sHHI8s8s')
            port = bswapword(port)
            addr = bswapdword(addr)
            assert family == 2 # AF_INET
            assert port >= 9000 and port <= 9014
            assert zero == b'\0\0\0\0\0\0\0\0'
            self.log('server transfer {}:{} with token {}, unk {}', ipaddress.ip_address(addr), port,
                    codecs.encode(token, 'hex'), codecs.encode(unk6, 'hex'))
            hdr.flags &= ~0x00000800

        if hdr.flags & 0x00001000:
            numsequences = r.readint()
            sequences = [r.readint() for i in range(numsequences)]
            sequences = ' '.join(['{:x}'.format(s) for s in sequences])
            self.log('  [00001000] request retransmit {}', sequences)
            hdr.flags &= ~0x00001000

        if hdr.flags & 0x00002000:
            # i think this happens when a packet is no longer relevant
            # (a position has since been updated at a higher sequence f.e.)
            numsequences = r.readint()
            sequences = [r.readint() for i in range(numsequences)]
            sequences = ' '.join(['{:x}'.format(s) for s in sequences])
            self.log('  [00002000] reject retransmit {}', sequences)
            hdr.flags &= ~0x00002000

        if hdr.flags & 0x00004000:
            sequence = r.readint()
            self.log('  [00004000] ack sequence {:x}', sequence)
            hdr.flags &= ~0x00004000

        if hdr.flags & 0x00008000:
            self.log('  [00008000] disconnect')
            hdr.flags &= ~0x00008000

        if hdr.flags & 0x00400000:
            unk5 = r.readformat('8s')
            # i've only seen this once, in packetloss2.pcap
            # i really haven't a client what it is...
            self.log('  [00400000] {} ==================', codecs.encode(unk5, 'hex'))
            hdr.flags &= ~0x00400000

        if hdr.flags & 0x01000000:
            # used by the server to detect speed hacking
            time = r.readformat('d')
            self.log('  [01000000] time {}', time)
            hdr.flags &= ~0x01000000
            actual_time = time - self.begin_time
            calc_time = self.pkt_time - self.session_time
            assert abs(actual_time - calc_time) < 1.0

        if hdr.flags & 0x02000000:
            # Ping time is based in the overall time the client started, not a particular session!
            self.last_ping = r.readformat('f')
            self.log('  [02000000] ping {:.2f}', self.last_ping)
            hdr.flags &= ~0x02000000
            assert abs(self.last_ping - self.pkt_time) < 1.0

        if hdr.flags & 0x04000000:
            ping_time = r.readformat('f')
            ping_result = r.readformat('f') # a delta maybe?
            self.log('  [04000000] pong {:.2f} {:.2f}', ping_time, ping_result)
            hdr.flags &= ~0x04000000
            # may fail is a ping is dropped
            #assert ping_time == self.last_ping

        if hdr.flags & 0x08000000:
            # this bit essentially says "up to your packet with time t i've seen n bytes (since the last time I send this)"
            numbytes = r.readint()
            time = r.readshort()
            self.log('  [08000000] ack {:08x} bytes on or before time {:04x}', numbytes, time)
            hdr.flags &= ~0x08000000
            if self.pkt_source == 'server':
                self.client_bytes += numbytes
                #self.log('    calc {:x} actual {:x}, diff {:x}', self.calc_client_bytes, self.client_bytes, self.client_bytes - self.calc_client_bytes)
            else:
                self.server_bytes += numbytes
                #self.log('    calc {:x} actual {:x}, diff {:x}', self.calc_server_bytes, self.server_bytes, self.server_bytes - self.calc_server_bytes)

        if hdr.flags & 0x00000004:
            while len(r):
                senderId = r.readint()
                receiverId = r.readint()
                fragmentCount = r.readshort()
                fragmentLength = r.readshort()
                fragmentIndex = r.readshort()

                # I suspect flags here are these:
                # 0001 npfChecksumEncrypted
                # 0002 npfHasTimeSensitiveHeaders
                # 0004 npfHasSequencedData
                # 0008 npfHasHighPriorityHeaders
                flags = r.readshort()
                assert fragmentIndex < fragmentCount
                assert flags >= 2 and flags <= 10

                self.log('  [00000004] fragment {:08x}, {:08x}, {:04x}, {:04x}, {:04x}, {:04}'.format(
                    senderId, receiverId, fragmentCount, fragmentLength, fragmentIndex, flags))

                if fragmentIndex == 0:
                    messageType = r.readint()

                    if messageType == 0xF7B0:
                        r.readint() # objectid
                        r.readint() # sequence
                        submessageType = r.readint()
                        self.log('  [00000004] message WEENIE_ORDERED {:04x} {}',
                            submessageType, messagenames.get(submessageType, 'Unknown'))
                        r.skip(fragmentLength - 32)
                    elif messageType == 0xF7B1:
                        r.readint() # sequence
                        submessageType = r.readint()
                        self.log('  [00000004] message ORDERED {:04x} {}',
                            submessageType, messagenames.get(submessageType, 'Unknown'))
                        r.skip(fragmentLength - 28)
                    else:
                        self.log('  [00000004] message {:04x} {}',
                            messageType, messagenames.get(messageType, 'Unknown'))
                        r.skip(fragmentLength - 20)
                    stats.log(messageType, self.pkt_source, flags)
                else:
                    r.skip(fragmentLength - 16)
            hdr.flags &= ~0x00000004

        if hdr.flags != 0:
            raise RuntimeError('Unknown flags: {:08x}'.format(hdr.flags))

