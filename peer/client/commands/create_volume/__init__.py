import sys
from getopt import getopt
from getopt import GetoptError

from peer.client.main import get_http_connection
from peer.client.common import config

VOLUME_TYPES = ['nfs']


def usage():
    sys.stdout.write('''Usage: %s [...] cv [OPTIONS]

Create a new volume

Options:
    -h, --help                    print usage
    -n, --name=<random>           volume name
    -t, --type=nfs                volume type [nfs]

''' % sys.argv[0])
    sys.exit(1)


def parse_args(argv):
    cfg = config.load()

    try:
        opts, args = getopt(argv, 'hnt', ['help', 'name', 'type'])
    except GetoptError as ex:
        usage()

    cfg.set('type', 'nfs')

    for k, v in opts:
        if k in ('-h', '--help'):
            usage()
        elif k in ('-n', '--name'):
            cfg.set('name', v)
        elif k in ('-t', '--type'):
            cfg.set('type', v)

    return args


def create_volume(argv):
    argv = parse_args(argv)

    if cfg.type not in VOLUME_TYPES:
        usage()

    body = {
        'volume': {
            'type': cfg.type
        }
    }
    if 'name' in cfg:
        body['volume']['name'] = cfg.name

    conn = get_http_connection()

    conn.request('POST', '/v1/action/cv', body=body)
    res = conn.getresponse()

    if res.status == 200:
        sys.stdout.write('''Create New Volume: %s
''' % res.json['_id'])
    else:
        sys.stderr.write('''Create New Volume Failed
''')


NAME = 'cv'
COMMAND = create_volume
