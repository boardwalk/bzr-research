import ipaddress
import codecs
import struct
import sys
from header import Header
from reader import Reader
from checksumxorgenerator import ChecksumXorGenerator

#0x00000100 <256,COnePrimHeader<256,96,CServerSwitchStruct> >
#0x00000200 <512,COnePrimHeader<512,7,sockaddr_in> >
#0x00000400 <1024,CEmptyHeader<1024,7> >
#0x00000800 <2048,COnePrimHeader<2048,1073741922,CReferralStruct> >
#0x00001000 <4096,CSeqIDListHeader<4096,33> >
#0x00002000 <8192,CSeqIDListHeader<8192,33> >
#0x00004000 <16384,COnePrimHeader<16384,1,unsigned long> >
#0x00008000 <32768,CEmptyHeader<32768,3> >
#0x00010000 <65536,CLogonHeader>
#0x00020000 <131072,COnePrimHeader<131072,7,unsigned __int64> >
#0x00040000 <262144,CConnectHeader>
#0x00080000 <524288,COnePrimHeader<524288,536870919,unsigned __int64> >
#0x00100000 <1048576,CPackObjHeader<NetError,1048576,7> >
#0x00200000 <2097152,CPackObjHeader<NetError,2097152,2> >
#0x00400000 <4194304,COnePrimHeader<4194304,7,CICMDCommandStruct> >
#0x01000000 <16777216,CTimeSyncHeader>
#0x02000000 <33554432,CEchoRequestHeader>
#0x04000000 <67108864,CEchoResponseHeader>
#0x08000000 <134217728,COnePrimHeader<134217728,16,CFlowStruct> >
#
#sym name: ohfDisposable has type -OptionalHeaderFlags has value 0001
#sym name: ohfExclusive has type -OptionalHeaderFlags has value 0002
#sym name: ohfNotConn has type -OptionalHeaderFlags has value 0004
#sym name: ohfTimeSensitive has type -OptionalHeaderFlags has value 0008
#sym name: ohfShouldPiggyBack has type -OptionalHeaderFlags has value 0010
#sym name: ohfHighPriority has type -OptionalHeaderFlags has value 0020
#sym name: ohfCountsAsTouch has type -OptionalHeaderFlags has value 0040
#sym name: ohfEncrypted has type -OptionalHeaderFlags has value 20000000
#sym name: ohfSigned has type -OptionalHeaderFlags has value 40000000

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
    header = data[:20]
    header[8:12] = b'\xDD\x70\xDD\xBA'
    return checksumdata(header, True)

def checksumcontent(hdr, data):
    if hdr.flags & 0x00000004:
        r = Reader(data)
        if hdr.flags & 0x00000100:
            r.skip(8)
        if hdr.flags & 0x00001000:
            nseq = r.readint()
            r.skip(nseq * 4)
        if hdr.flags & 0x00002000:
            nseq = r.readint()
            r.skip(nseq * 4)
        if hdr.flags & 0x00004000:
            r.skip(4)
        if hdr.flags & 0x00400000:
            r.skip(8)
        if hdr.flags & 0x01000000:
            r.skip(8)
        if hdr.flags & 0x02000000:
            r.skip(4)
        if hdr.flags & 0x04000000:
            r.skip(8)
        if hdr.flags & 0x08000000:
            r.skip(6)
        checksum = checksumdata(data[0 : r.position], True)

        while len(r):
            frag_start = r.position
            r.readint()
            r.readint()
            r.readshort()
            frag_len = r.readshort()
            r.readshort()
            r.readshort()
            r.skip(frag_len - 16)

            frag_checksum = checksumdata(data[frag_start : frag_start + frag_len], True)
            checksum = (checksum + frag_checksum) & 0xFFFFFFFF

        return checksum
    else:
        return checksumdata(data, True)

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


REVERSE_COLOR = b'\x1b[7m'
POSITIVE_COLOR = b'\x1b[27m'
RESET_COLOR = b'\x1b[0m'

class Session(object):
    def __init__(self, num, name, time):
        self.num = num
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
        if self.num < 6:
            color = b'\x1b' + '[{};1m'.format(31 + self.num).encode('utf-8')
        else:
            color= RESET_COLOR
        sys.stdout.buffer.write(color)
        sys.stdout.buffer.write(self.name.encode('utf-8'))
        sys.stdout.buffer.write(b' ')
        if self.pkt_source == 'server':
            sys.stdout.buffer.write(REVERSE_COLOR)
        sys.stdout.buffer.write(self.pkt_source.encode('utf-8'))
        if self.pkt_source == 'server':
            sys.stdout.buffer.write(POSITIVE_COLOR)
        sys.stdout.buffer.write(b' ')
        sys.stdout.buffer.write(fmt.format(*args, **kwargs).encode('utf-8'))
        sys.stdout.buffer.write(b'\n')

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

        calc_checksum = checksumheader(pkt_data) + (checksumcontent(hdr, pkt_data[20:]) ^ xor_val) & 0xFFFFFFFF
        if calc_checksum != hdr.checksum:
            self.log('======= FAIL ====== {:08x}', calc_checksum)

        if hdr.flags == 0x00010000:
            self.handle_logon(hdr, r)
        elif hdr.flags == 0x00020000:
            # uint64_t (7)
            self.handle_referred(hdr, r)
        elif hdr.flags == 0x00040000:
            # CConnectHeader
            self.handle_connect(hdr, r)
        elif hdr.flags == 0x00080000:
            # uint64_t (20000007)
            self.handle_connect_reply(hdr, r)
        else:
            self.handle_pkt(hdr, r)

        assert len(r) == 0

    def handle_logon(self, hdr, r):
        self.log('  [00010000] logon')

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

    def handle_referred(self, hdr, r):
        token = r.readformat('Q')
        self.log('  [00020000] referred with token {:016x}', token)

    def handle_connect(self, hdr, r):
        self.server_endpoint = hdr.endpoint
        self.session = hdr.session

        # appears to be "seconds since Asheron's Call epoch"
        # where the epoch is approximately 1995-09-27 06:00 UTC
        self.begin_time = r.readformat('d')

        # the value the client should use in client_hello_reply
        token = r.readformat('Q')

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

        self.log('  [00040000] connect with token {:016x}, server seed {:08x}, client seed {:08x}',
            token, serverseed, clientseed)

    def handle_connect_reply(self, hdr, r):
        token = r.readformat('Q')
        self.log('  [00080000] connect reply with token {:016x}', token)

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
            # CServerSwitchStruct
            unk0 = r.readformat('8s')
            self.log('  [00000100] server switch {}', codecs.encode(unk0, 'hex'))
            hdr.flags &= ~0x00000100

        if hdr.flags & 0x00000200:
            # sockaddr_in (7)
            assert False

        if hdr.flags & 0x00000400:
            # EmptyHeader (7)
            assert False

        if hdr.flags == 0x00000800:
            # CReferralStruct
            token, family, port, addr, zero, unk6 = r.readformat('QHHI8s8s')
            port = bswapword(port)
            addr = bswapdword(addr)
            assert family == 2 # AF_INET
            assert port >= 9000 and port <= 9014
            assert zero == b'\0\0\0\0\0\0\0\0'
            self.log('  [00000800] server referral {}:{} with token {:016x}, unk {}', ipaddress.ip_address(addr), port,
                    token, codecs.encode(unk6, 'hex'))
            hdr.flags &= ~0x00000800

        if hdr.flags & 0x0001000:
            # SeqIDList (33)
            numsequences = r.readint()
            sequences = [r.readint() for i in range(numsequences)]
            sequences = ' '.join(['{:x}'.format(s) for s in sequences])
            self.log('  [00001000] request retransmit {}', sequences)
            hdr.flags &= ~0x00001000

        if hdr.flags & 0x00002000:
            # SeqIDList (33)
            # i think this happens when a packet is no longer relevant
            # (a position has since been updated at a higher sequence f.e.)
            numsequences = r.readint()
            sequences = [r.readint() for i in range(numsequences)]
            sequences = ' '.join(['{:x}'.format(s) for s in sequences])
            self.log('  [00002000] reject retransmit {}', sequences)
            hdr.flags &= ~0x00002000

        if hdr.flags & 0x00004000:
            # unsigned long (1)
            sequence = r.readint()
            self.log('  [00004000] ack sequence {:x}', sequence)
            hdr.flags &= ~0x00004000

        if hdr.flags & 0x00008000:
            # EmptyHeader (3)
            self.log('  [00008000] disconnect')
            hdr.flags &= ~0x00008000

        if hdr.flags & 0x00100000:
            # PackObjHeader<NetError> (7)
            assert False

        if hdr.flags & 0x00200000:
            # PackObjHeader<NetError> (2)
            assert False

        if hdr.flags & 0x00400000:
            # CICMDCommandStruct (7)
            # CI "character info"?
            unk5 = r.readformat('8s')
            self.log('  [00400000] {} ==================', codecs.encode(unk5, 'hex'))
            hdr.flags &= ~0x00400000

        if hdr.flags & 0x01000000:
            # CTimeSyncHeader
            # used by the server to detect speed hacking
            time = r.readformat('d')
            self.log('  [01000000] time {}', time)
            hdr.flags &= ~0x01000000
            actual_time = time - self.begin_time
            calc_time = self.pkt_time - self.session_time
            assert abs(actual_time - calc_time) < 1.0

        if hdr.flags & 0x02000000:
            # CEchoRequestHeader
            # Ping time is based in the overall time the client started, not a particular session!
            self.last_ping = r.readformat('f')
            self.log('  [02000000] ping {:.2f}', self.last_ping)
            hdr.flags &= ~0x02000000
            assert abs(self.last_ping - self.pkt_time) < 1.0

        if hdr.flags & 0x04000000:
            # EchoResponseHeader
            ping_time = r.readformat('f')
            ping_result = r.readformat('f') # a delta maybe?
            self.log('  [04000000] pong {:.2f} {:.2f}', ping_time, ping_result)
            hdr.flags &= ~0x04000000
            # may fail is a ping is dropped
            #assert ping_time == self.last_ping

        if hdr.flags & 0x08000000:
            # CFlowStruct
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

