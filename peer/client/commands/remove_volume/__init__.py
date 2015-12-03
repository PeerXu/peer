import sys
from getopt import getopt
from getopt import GetoptError

from peer.client.main import get_http_connection


def usage():
    sys.stdout.write('''Usage: %s [...] rmv [OPTIONS] <volume>

Remove volume

Options:
    -h, --help                    print usage

Arguments:
    volume                        volume id  [require]

''' % sys.argv[0])
    sys.exit(1)


def parse_args(argv):
    try:
        opts, args = getopt(argv, 'h', ['help'])
    except GetoptError:
        usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            usage()

    return args


def rm_volume(argv):
    argv = parse_args(argv)

    if len(argv) != 1:
        usage()

    volume_id = argv[0]

    conn = get_http_connection()

    body = {
        'volume': {
            '_id': volume_id
        }
    }

    conn.request('POST', '/v1/action/rmv', body=body)
    res = conn.getresponse()

    if res.status == 204:
        sys.stdout.write('''Delete Volume: %s
''' % volume_id)
    else:
        sys.stderr.write('''Delete Volume: %s Failed
''' % volume_id)


NAME = 'rmv'
COMMAND = rm_volume
