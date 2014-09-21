
class LoginSession(object):
    def __init__(self):
        print('new login session')
        
    def handle_client(self, r):
        print('client login message')

    def handle_server(self, r):
        print('server login message')
