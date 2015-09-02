import sys
from getopt import getopt
from getopt import GetoptError

from peer.server.common import options as server_options
from peer.client.common import options as client_options
from peer.common.usage import usage
from peer.server.main import main as server_main
from peer.client.main import main as client_main

SERVER_OPTIONS = server_options.OPTIONS
CLIENT_OPTIONS = client_options.OPTIONS

def main():
    argv = sys.argv
    mode = 'client'
    daemon = True

    try:
        opts, args = getopt(argv[1:], 'hDH:P:', ['help', 'debug', 'host=', 'port='])
    except GetoptError as ex:
        usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            usage()
        elif k in ('-D', '--debug'):
            mode = 'server'
            SERVER_OPTIONS['daemon'] = False
        elif k in ('-H', '--host'):
            {'server': SERVER_OPTIONS,
             'client': CLIENT_OPTIONS}.get(mode, {})['host'] = v
        elif k in ('-P', '--port'):
            {'server': SERVER_OPTIONS,
             'client': CLIENT_OPTIONS}.get(mode, {})['port'] = int(v)

    {'server': server_main,
     'client': client_main}[mode](argv[1:])

if __name__ == '__main__':
    main()
