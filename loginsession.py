import ipaddress
import codecs

def readstring(r):
    size = r.readshort()
    s = r.readformat('{}s'.format(size))
    r.align()
    return s

class LoginSession(object):
    def __init__(self):
        self.state = 'hello'
        print('new login session')

    def handle_client(self, r):
        handler = getattr(self, 'handle_client_' + self.state)
        handler(r)

    def handle_server(self, r):
        handler = getattr(self, 'handle_server_' + self.state)
        handler(r)

    def handle_client_hello(self, r):
        print('handle_client_hello')

        sequence = r.readint()
        flags = r.readint()
        crc = r.readint()
        unk1 = r.readshort()
        unk2 = r.readshort()
        size = r.readshort()
        session = r.readshort()
        assert sequence == 0
        assert flags == 0x00010000
        # TODO crc
        assert unk1 == 0
        assert unk2 == 0
        assert size == len(r)
        assert session == 0

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

        assert version == b'1802'
        assert unk3 == 0x0126
        assert unk4 == 0
        assert unk5 == 2
        assert unk6 == 0x4000
        assert unk7 == 0
        assert unk8 == 0
        assert unk9 == 0
        assert accountkeylen == 246
        assert len(r) == 0

        self.state = 'hello2'

    def handle_client_hello2(self, r):
        # the client repeats itself!
        self.handle_client_hello(r)

    def handle_server_hello2(self, r):
        print('handle_server_hello2')

        sequence = r.readint()
        flags = r.readint()
        crc = r.readint()
        unk1 = r.readshort()
        unk2 = r.readshort()
        size = r.readshort()
        session = r.readshort()

        assert sequence == 0
        assert flags == 0x00040000
        # TODO unk1
        assert unk2 == 0
        assert size == len(r)
        self.session = session

        unk3 = r.readformat('8s')
        unixtime = r.readint()
        unkip = r.readint()
        unk4 = r.readint()
        unk5 = r.readformat('8s')
        unk6 = r.readint()

        assert unk4 == 10
        assert unk6 == 0

        print('unk3 = {} unk5 = {}'.format(codecs.encode(unk3, 'hex'), codecs.encode(unk5, 'hex')))

        self.state = 'hello3'

    def handle_client_hello3(self, r):
        print('handle_client_hello3')

        sequence = r.readint()
        flags = r.readint()
        crc = r.readint()
        unk1 = r.readshort()
        unk2 = r.readshort()
        size = r.readshort()
        session = r.readshort()

        assert sequence == 0
        assert flags == 0x00080000
        # TODO unk1
        assert unk2 == 0
        assert size == len(r)
        assert session == self.session

        unk3 = r.readformat('8s')

        self.state = 'hello4'

    def handle_client_hello4(self, r):
        # the client repeats itself!
        self.handle_client_hello3(r)

    def handle_server_hello4(self, r):
        self.state = 'connected'
        self.handle_server_connected(r)

    def handle_client_connected(self, r):
        print('handle_client_connected')
        r.dump()

    def handle_server_connected(self, r):
        print('handle_server_connected')
        r.dump()

# 00 00 00 00|00 00 01 00|73 20 b3 7a|00 00|00 00|32 01|00 00|04 00 31 38 30 32|00 00 26 01 00 00 ........s .z....2.....1802..&...
# 02 00 00 40 00 00 00 00 d4 36 1e 54 19 00 6d 64 39 6e 71 39 6d 33 6e 6a 78 6a 6c 70 64 63 77 79 ...@.....6.T..md9nq9m3njxjlpdcwy
# 34 61 6e 71 64 6e 71 00 00 00 00 00 f6 00 00 00 80 f4 6a 41 41 41 41 41 45 43 41 41 41 42 61 41 4anqdnq...........jAAAAAECAAABaA
# 41 41 41 4b 51 41 41 49 63 41 68 61 43 78 38 57 69 63 6b 51 49 68 2f 6a 57 6f 6f 76 32 6b 51 55 AAAKQAAIcAhaCx8WickQIh/jWoov2kQU
# 35 44 38 78 4c 6f 61 46 68 2f 51 77 73 57 33 48 49 71 63 51 62 44 73 65 32 6e 48 43 4e 44 64 4c 5D8xLoaFh/QwsW3HIqcQbDse2nHCNDdL
# 65 51 53 63 61 4f 66 67 53 57 61 77 6b 58 39 46 4a 4c 4b 57 61 79 59 6a 63 6c 44 71 53 47 4e 4c eQScaOfgSWawkX9FJLKWayYjclDqSGNL
# 33 31 49 74 54 54 54 6d 69 61 47 51 51 5a 67 51 44 54 44 6d 6c 64 66 6c 7a 62 6f 71 42 56 2b 42 31ItTTTmiaGQQZgQDTDmldflzboqBV+B
# 6a 48 6a 4e 58 75 44 2f 4f 47 71 45 35 52 37 35 48 2b 6a 62 62 58 38 6e 71 35 45 64 4f 71 79 6e jHjNXuD/OGqE5R75H+jbbX8nq5EdOqyn
# 71 4f 6f 4f 46 46 46 58 73 78 62 71 66 79 64 6b 52 6d 49 51 41 41 41 47 31 42 77 35 55 58 6c 49 qOoOFFFXsxbqfydkRmIQAAAG1Bw5UXlI
# 68 48 35 47 75 47 75 63 33 52 68 36 45 74 4e 37 34 76 53 39 4d 63 4e 30 62 32 4e 48 6f 41 38 46 hH5GuGuc3Rh6EtN74vS9McN0b2NHoA8F
# 38 61 38 51 3d 3d                                                                               8a8Q==
