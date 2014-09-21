
class WorldSession(object):
    def __init__(self):
        print('new world session')

    def handle_client(self, r):
        print('client world message')
        r.dump()

    def handle_server(self, r):
        print('server world message')
        r.dump()
