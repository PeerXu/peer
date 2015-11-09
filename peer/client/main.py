import os
import tempfile

import sys
from getopt import getopt
from getopt import GetoptError

from peer.common.usage import usage
from peer.common import options
from peer.client.commands import load_commands
from peer.client.common.utils import get_http_connection

OPTIONS = options.OPTIONS

def ps_containers(argv):
    conn = get_http_connection()
    conn.request('GET', '/v1/containers?embedded={"application":1}')
    res = conn.getresponse()

    containers = res.json['_items']
    print 'Containers:'
    print '%-24s | %-20s | %-8s | %-16s' % ('ID', 'Name', 'Status', 'Application')
    print '-' * 78
    for container in containers:
        print '%-24s | %-20s | %-8s | %-16s' % (container['_id'],
                                                container['name'][:20],
                                                container['status'],
                                                container['application']['program'])
    conn.close()

def commit_container(argv):
    argv = parse_args_commit_container(argv)
    if len(argv) != 3:
        commit_container_usage()

    container_id, application_name, application_program = argv

    conn = get_http_connection()

    conn.request('POST', '/v1/action/commit',
                 body={'container': {'_id': container_id},
                       'application': {'name': application_name,
                                       'program': application_program}})

    res = conn.getresponse()

    if res.json['status'] == 'commiting':
        sys.stdout.write('''Commiting Container: %s to Application: (%s, %s)
''' % (container_id, application_name, application_program))
    else:
        sys.stdout.write('''Commiting Container: %s Failed
''' % container_id)

def parse_args_commit_container(argv):
    try:
        opts, args = getopt(argv, 'h', ['help'])
    except GetoptError as ex:
        commit_container_usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            commit_container_usage()

    return args

def commit_container_usage():
    sys.stdout.write('''Usage: %s [...] commit [OPTIONS] <container> <name> <program>

Create a new application from a existed container

Options:
    -h, --help                    print usage

Arguments:
    container                     container id  [require]
    name                          application name  [require]
    program                       application program  [require]

''' % sys.argv[0])
    sys.exit(1)

def start_container(argv):
    argv = parse_args_start_container(argv)
    if len(argv) != 1:
        start_container_usage()

    container_id = argv[0]

    conn = get_http_connection()

    conn.request('POST', '/v1/action/start',
                 body={'container': {'_id': container_id}})

    res = conn.getresponse()

    if res.status == 200:
        sys.stdout.write('''Start Container: %s
''' % container_id)
    else:
        sys.stdout.write('''Start Container: %s Failed
''' % container_id)

def parse_args_start_container(argv):
    try:
        opts, args = getopt(argv, 'h', ['help'])
    except GetoptError as ex:
        start_container_usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            start_container_usage()

    return args

def start_container_usage():
    sys.stdout.write('''Usage: %s [...] start <container>

Start container

Options:
    -h, --help                    print usage

Arguments:
    container                     container id  [require]

''' % sys.argv[0])
    sys.exit(1)

def stop_container(argv):
    argv = parse_args_stop_container(argv)
    if len(argv) != 1:
        stop_container_usage()

    container_id = argv[0]

    conn = get_http_connection()

    conn.request('POST', '/v1/action/stop',
                 body={'container': {'_id': container_id}})

    res = conn.getresponse()

    if res.status == 200:
        sys.stdout.write('''Stop Container: %s
''' % container_id)
    else:
        sys.stdout.write('''Stop Container: %s Failed, %s, %s
''' % (container_id, res.reason, res.read()))

def parse_args_stop_container(argv):
    try:
        opts, args = getopt(argv, 'h', ['help'])
    except GetoptError as ex:
        stop_container_usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            stop_container_usage()

    return args

def stop_container_usage():
    sys.stdout.write('''Usage: %s [...] stop <container>

Stop container

Options:
    -h, --help                    print usage

Arguments:
    container                     container id  [require]

''' % sys.argv[0])
    sys.exit(1)

def rm_container(argv):
    argv = parse_args_rm_container(argv)
    if len(argv) != 1:
        rm_container_usage()

    container_id = argv[0]

    conn = get_http_connection()

    conn.request('POST', '/v1/action/rm',
                 body={'container': {'_id': container_id}})

    res = conn.getresponse()

    if res.status == 204:
        sys.stdout.write('''Remove Container: %s
''' % container_id)
    else:
        sys.stdout.write('''Remove Container: %s Failed
''' % container_id)

def parse_args_rm_container(argv):
    try:
        opts, args = getopt(argv, 'h', ['help'])
    except GetoptError as ex:
        rm_container_usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            rm_container_usage()

    return args

def rm_container_usage():
    sys.stdout.write('''Usage: %s [...] rm <container>

Remove container

Options:
    -h, --help                    print usage

Arguments:
    container                     container id  [require]

''' % sys.argv[0])
    sys.exit(1)

def run_container(argv):
    argv = parse_args_run_container(argv)

    if len(argv) != 1:
        run_container_usage()

    application_id = argv[0]
    container_name = OPTIONS.get('name')
    autoremove = OPTIONS.get('autoremove', False)

    body = {
        'application': {'_id': application_id},
        'container': {
            'autoremove': autoremove,
            'volumes': OPTIONS['volumes']
        }
    }
    if container_name:
        body['container']['name'] = container_name

    conn = get_http_connection()

    conn.request('POST', '/v1/action/run', body=body)

    res = conn.getresponse()

    if res.status == 200:
        sys.stdout.write('''Run Application %s
''' % application_id)
    else:
        sys.stdout.write('''Run Application %s Failed
''' % application_id)

def parse_args_run_container(argv):
    try:
        opts, args = getopt(argv, 'hrv:', ['help', 'autoremove', 'volume='])
    except GetoptError as ex:
        run_container_usage()

    OPTIONS['volumes'] = []
    for k, v in opts:
        if k in ('-h', '--help'):
            run_container_usage()
        elif k in ('-n', '--name'):
            OPTIONS['name'] = v
        elif k in ('-r', '--autoremove'):
            OPTIONS['autoremove'] = True
        elif k in ('-v', '--volume'):
            if ':' not in v:
                run_container_usage()
            volume_id, drive = v.split(':', 1)
            OPTIONS['volumes'].append({
                'volume': volume_id,
                'drive': drive
            })

    return args

def run_container_usage():
    sys.stdout.write('''Usage: %s [...] run [OPTIONS] <application>

Create a new container from application and start it

Options:
    -h, --help                    print usage
    -n, --name=<random>           container name
    -r, --autoremove=false        auto remove when stop container
    -v, --volume=[]               bind mount a volume

Arguments:
    application                   application id  [require]

''' % sys.argv[0])
    sys.exit(1)

def ps_applications(argv):
    conn = get_http_connection()
    conn.request('GET', '/v1/applications')
    res = conn.getresponse()

    applications = res.json['_items']
    print 'Applications:'
    print '%-24s | %-16s | %-20s | %-16s' % ('ID', 'Name', 'Program', 'Cmdline')
    print '-' * 78
    for application in applications:
        print '%-24s | %-16s | %-20s | %-16s' % (application['_id'],
                                                 application['name'],
                                                 application['program'],
                                                 application['cmdline'])

def parse_args(opts, args):
    for k, v in opts:
        if k in ('-h', '--help'):
            usage()
        elif k in ('-H', '--host'):
            OPTIONS['host'] = v
            continue
        elif k in ('-P', '--port'):
            OPTIONS['port'] = int(v)

def main(argv):
    try:
        opts, args = getopt(argv, 'hH:P:', ['help', 'host=', 'port='])
    except GetoptError as ex:
        usage()

    parse_args(opts, args)
    if len(args) < 1:
        usage()

    action = args[0]

    COMMANDS = {
        'applications': ps_applications,
        'commit': commit_container,
        'start': start_container,
        'stop': stop_container,
        'run': run_container,
        'rm': rm_container,
        'ps': ps_containers,
    }

    COMMANDS.update(load_commands())

    COMMANDS.get(action, lambda *args, **kwargs: usage())(args[1:])
