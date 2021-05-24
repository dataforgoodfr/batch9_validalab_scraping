from twisted.internet import reactor
from txjsonrpc.web.jsonrpc import Proxy

version = '0.2'
version_info = 'validalab-scraping'


def print_value(value):
    import pprint
    pprint.pprint(value)


def print_error(error):
    print(' !! ERROR: ', error)


def shutdown():
    reactor.stop()


class HypheConnection:
    def __init__(self, address):
        self.proxy = Proxy(address)

    def run_command(self, command, args):
        d = self.proxy.callRemote(command, *args)
        d.addCallback(print_value).addErrback(print_error)
        d.addCallback(shutdown)
        reactor.run()
