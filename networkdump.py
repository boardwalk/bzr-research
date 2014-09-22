import ipaddress
import sys
import struct
from reader import Reader
from session import Session

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
    return network

def read_record_header(f):
    fmt = 'IIII'
    data = read_exact(f, struct.calcsize(fmt))
    ts_sec, ts_usec, incl_len, orig_len = struct.unpack(fmt, data)
    #print('{} {}'.format(ts_sec, ts_usec))
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

def handle_packet(linktype, data, sessions):
    r = Reader(data)

    if linktype == 101: # LINKTYPE_RAW, no header!
        pass
    elif linktype == 113: # LINKTYE_LINUX_SLL
        pktype = r.readformat('!H')
        reallinktype = r.readformat('!H')
        linkaddrlen = r.readformat('!H')
        linkaddr = r.readformat('8s')
        prototype = r.readformat('!H')
        assert reallinktype == 1 # ARPHRD_ETHER
        assert linkaddrlen <= 8
        assert prototype == 0x800 # EtherType IPv4

        # 0 means 'sent to us'
        # 4 means 'sent by us'
        # we get two copies of each packet, one *before* NAT, and one *after*
        # while picking 0 or 4 always will have either our local ip as the real client or the nat,
        # depending on whether the packet is incoming or outgoing
        # we only key our session on server ip, not local ip
        if pktype != 0:
            return
    else:
        raise RuntimeError('unknown linktype')

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
        session = Session(key)
        sessions[key] = session

    if srcip.is_private:
        session.handle_client_pkt(r)
    else:
        session.handle_server_pkt(r)

def main():
    f = sys.stdin.buffer.raw
    sessions = {}
    linktype = read_file_header(f)
    while True:
        try:
            size = read_record_header(f)
        except EOFError:
            break
        handle_packet(linktype, read_exact(f, size), sessions)

if __name__ == '__main__':
    main()
