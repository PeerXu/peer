import sys
from getopt import getopt
from getopt import GetoptError

from peer.client.main import get_http_connection


def usage():
    sys.stdout.write('''Usage: %s [...] applications [OPTIONS]

List applications

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


def application_display_repository(app):
    return '{0}/{1}'.format(app['namespace'], app['repository']) if app['namespace'] != 'library' else app['repository']


def ps_applications(argv):
    argv = parse_args(argv)

    conn = get_http_connection()
    conn.request('GET', '/v1/applications')
    res = conn.getresponse()

    applications = res.json['_items']
    print 'Applications:'
    print '%-24s | %-16s | %-20s | %-16s' % ('ID', 'Repository', 'Program', 'Cmdline')
    print '-' * 78
    for application in applications:
        print '%-24s | %-16s | %-20s | %-16s' % (application['_id'],
                                                 application_display_repository(application),
                                                 application['config']['program'],
                                                 application['config']['cmdline'])

NAME = 'applications'
COMMAND = ps_applications
