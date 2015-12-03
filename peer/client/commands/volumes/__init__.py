import sys
from getopt import getopt
from getopt import GetoptError

from peer.client.main import get_http_connection


def usage():
    sys.stdout.write('''Usage: %s [...] volumes

List volumes

Options:
    -h, --help                    print usage

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


def ps_volumes(argv):
    argv = parse_args(argv)

    conn = get_http_connection()
    conn.request('GET', '/v1/volumes')
    res = conn.getresponse()

    volumes = res.json['_items']
    print 'Volumes:'
    print '%-24s | %-20s | %-40s' % ('ID', 'Name', 'URI')
    print '-' * 78
    for volume in volumes:
        print '%-24s | %-20s | %-40s' % (volume['_id'],
                                         volume['name'][:20],
                                         volume['uri'])
    conn.close()


NAME = 'volumes'
COMMAND = ps_volumes
