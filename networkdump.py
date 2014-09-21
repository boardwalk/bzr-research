import ipaddress
import sys
import struct
from reader import Reader
from loginsession import LoginSession
from worldsession import WorldSession

def read_exact(f, size):
    data = bytearray()
    while len(data) < size:
        moredata = f.read(size - len(data))
        if not moredata:
            raise EOFError
        data.extend(moredata)
    return data

def read_file_header(f):
    fmt = 'IHHiIII'
    data = read_exact(f, struct.calcsize(fmt))
    magic_num, ver_major, ver_minor, thiszone, sigfigs, snaplen, network = struct.unpack(fmt, data)
    assert magic_num == 0xa1b2c3d4
    assert ver_major == 2
    assert ver_minor == 4
    assert network == 101 # LINKTYPE_RAW

def read_record_header(f):
    fmt = 'IIII'
    data = read_exact(f, struct.calcsize(fmt))
    ts_sec, ts_usec, incl_len, orig_len = struct.unpack(fmt, data)
    assert incl_len == orig_len
    return incl_len

def handle_ip_header(r):
    version_ihl = r.readbyte()    
    dscp_ecn = r.readbyte()
    length = r.readformat('!H')
    iden = r.readformat('!H')
    flags_fragoff = r.readformat('!H')
    ttl = r.readbyte()
    proto = r.readbyte()
    checksum = r.readformat('!H')
    srcip = r.readformat('!I')
    dstip = r.readformat('!I')
    assert version_ihl >> 4 == 4
    assert length == len(r) + 20
    assert proto == 17 # IPPROTO_UDP
    r.skip((version_ihl & 0xF) * 4 - 20)
    return srcip, dstip

def handle_udp_header(r):
    srcport = r.readformat('!H')
    dstport = r.readformat('!H')
    length = r.readformat('!H')
    checksum = r.readformat('!H')
    assert length == len(r) + 8
    return srcport, dstport

def handle_packet(data, sessions):
    r = Reader(data)
    srcip, dstip = handle_ip_header(r)
    srcport, dstport = handle_udp_header(r)

    srcip = ipaddress.ip_address(srcip)
    dstip = ipaddress.ip_address(dstip)

    if srcip.is_private:
        svrip, svrport = dstip, dstport
    else:
        svrip, svrport = srcip, srcport

    key = "{}:{}".format(svrip, svrport & ~1)

    try:
        session = sessions[key]
    except KeyError:
        if svrport < 9008:
            session = LoginSession()
        else:
            session = WorldSession()

        sessions[key] = session

    if srcip.is_private:
        session.handle_client(r)
    else:
        session.handle_server(r)

def main():
    f = sys.stdin.buffer.raw
    sessions = {}
    read_file_header(f)
    while True:
        try:
            size = read_record_header(f)
        except EOFError:
            break
        handle_packet(read_exact(f, size), sessions)

if __name__ == '__main__':
    main()
