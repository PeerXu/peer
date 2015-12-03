import sys
from getopt import getopt
from getopt import GetoptError

from peer.common import config
from peer.common.usage import usage
from peer.server.main import main as server_main
from peer.client.main import main as client_main


def main():
    cfg = config.load()
    argv = sys.argv
    cfg.set('mode', 'client')
    cfg.set('daemon', True)

    try:
        opts, args = getopt(argv[1:], 'hDH:P:', ['help', 'debug', 'host=', 'port='])
    except GetoptError as ex:
        usage()

    for k, v in opts:
        if k in ['-h', '--help']:
            usage()
        elif k in ['-D', '--debug']:
            cfg.set('mode', 'server')
            cfg.set('daemon', False)
        elif k in ['-H', '--host']:
            cfg.set('host', v)
        elif k in ['-P', '--port']:
            cfg.set('port', int(v))

    {'server': server_main,
     'client': client_main}[cfg.mode](argv[1:])


if __name__ == '__main__':
    main()
