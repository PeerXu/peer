import sys
from getopt import getopt
from getopt import GetoptError

from peer.common import options
from peer.common.usage import usage
from peer.server.main import main as server_main
from peer.client.main import main as client_main

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
            options.SERVER_OPTIONS['daemon'] = False
        elif k in ('-H', '--host'):
            {'server': options.SERVER_OPTIONS,
             'client': options.CLIENT_OPTIONS}.get(mode, {})['host'] = v
        elif k in ('-P', '--port'):
            {'server': options.SERVER_OPTIONS,
             'client': options.CLIENT_OPTIONS}.get(mode, {})['port'] = int(v)

    {'server': server_main,
     'client': client_main}[mode](argv[1:])

if __name__ == '__main__':
    main()
