import sys
from getopt import getopt
from getopt import GetoptError

from peer.common import peerfile
from peer.common.peerfile.exception import PeerfileError
from peer.client.main import get_http_connection
from peer.client.common import config


def usage():
    sys.stdout.write('''Usage: %s [...] build [OPTIONS] <path>

Build an application from peerfile

Options:
    -h, --help                    print usage
    -r, --autoremove=true         remove container after successful build

Arguments:
    path                          path of peerfile

''' % sys.argv[0])
    sys.exit(1)


def parse_args(argv):
    cfg = config.load()

    try:
        opts, args = getopt(argv, 'hr', ['help', 'autoremove'])
    except GetoptError:
        usage()

    cfg.set('autoremove', True)
    for k, v in opts:
        if k in ('-h', '--help'):
            usage()
        elif k in ('-r', '--autoremove'):
            cfg.set('autoremove', not v.lower().startswith('f'))

    return args


def build_application(argv):
    cfg = config.load()
    argv = parse_args(argv)

    if len(argv) != 1:
        usage()

    path = argv[0]

    try:
        pf = peerfile.parse(path)
    except PeerfileError as ex:
        sys.stderr.write(str(ex) + '\n')
        sys.exit(255)

    body = {
        'application': {
            'name': pf['name'],
            'program': pf['program'],
            'cmdline': pf['cmdline'],
            'from': pf['from'],
            'min_core': pf.get('min_core', 1),
            'min_mem': pf.get('min_mem', 512)
        },
        'container': {
            'steps': pf['run'],
            'autoremove': cfg.autoremove
        }
    }

    conn = get_http_connection()

    conn.request('POST', '/v1/action/build', body=body)

    res = conn.getresponse()

    if res.status == 200:
        sys.stdout.write('''Building Application: %s
''' % body['application']['name'])
    else:
        sys.stdout.write('''Building Application: %s Failed
''' % body['application']['name'])


NAME = 'build'
COMMAND = build_application
