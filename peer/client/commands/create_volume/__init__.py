import sys
from getopt import getopt
from getopt import GetoptError

from peer.common import options
from peer.client.main import get_http_connection

OPTIONS = options.OPTIONS
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
    try:
        opts, args = getopt(argv, 'hnt', ['help', 'name', 'type'])
    except GetoptError as ex:
        usage()

    OPTIONS['type'] = 'nfs'

    for k, v in opts:
        if k in ('-h', '--help'):
            usage()
        elif k in ('-n', '--name'):
            OPTIONS['name'] = v
        elif k in ('-t', '--type'):
            OPTIONS['type'] = v

    return args

def create_volume(argv):
    argv = parse_args(argv)

    if OPTIONS['type'] not in VOLUME_TYPES:
        usage()

    body = {
        'volume': {
            'type': OPTIONS['type']
        }
    }
    if 'name' in OPTIONS:
        body['volume']['name'] = OPTIONS['name']

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
