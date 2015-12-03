import sys
from getopt import getopt
from getopt import GetoptError

from peer.client.main import get_http_connection
from peer.common.utils import parse_repository_name


def usage():
    sys.stdout.write('''Usage: %s [...] pull [OPTIONS] <name>[:<tag>]

Pull an application or a repository from a registry

Options:
    -h, --help                    print usage

Arguments:
    name                          download application or repository by name from registry
    tag                           download application or repository by name with tag from registry

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


def pull_application(argv):
    argv = parse_args(argv)

    if len(argv) != 1:
        usage()

    registry, namespace, repository, tag = parse_repository_name(argv[0])

    conn = get_http_connection()

    body = {
        'application': {
            'registry': registry,
            'namespace': namespace,
            'repository': repository,
            'tag': tag
        }
    }

    conn.request('POST', '/v1/action/pull', body=body)
    res = conn.getresponse()

    # TODO(Peer): need progress bar
    if res.status == 200:
        sys.stdout.write('''Pull Repository %s/%s:%s from %s
''' % (namespace, repository, tag, registry))
    else:
        sys.stderr.write('''Pull Repository %s/%s:%s from %s failed
''' % (namespace, repository, tag, registry))


NAME = 'pull'
COMMAND = pull_application
