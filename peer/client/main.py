import os
import httplib
import json
import tempfile

import sys
from getopt import getopt
from getopt import GetoptError

from peer.common import options
from peer.common.usage import usage

OPTIONS = options.CLIENT_OPTIONS

## about RDP FILE SETTINGS: http://www.donkz.nl/files/rdpsettings.html
RDP_CONNECTION_TEMPLATE = '''
screen mode id:i:2
use multimon:i:1
desktopwidth:i:1440
desktopheight:i:900
session bpp:i:32
winposstr:s:0,3,0,0,800,600
compression:i:1
keyboardhook:i:2
audiocapturemode:i:0
videoplaybackmode:i:1
connection type:i:6
displayconnectionbar:i:1
disable wallpaper:i:1
allow font smoothing:i:1
allow desktop composition:i:0
disable full window drag:i:1
disable menu anims:i:1
disable themes:i:0
disable cursor setting:i:0
bitmapcachepersistenable:i:1
full address:s:{address}
audiomode:i:0
redirectprinters:i:1
redirectcomports:i:0
redirectsmartcards:i:1
redirectclipboard:i:1
redirectposdevices:i:0
redirectdirectx:i:1
autoreconnection enabled:i:1
authentication level:i:2
prompt for credentials:i:0
prompt for credentials on client:i:0
negotiate security layer:i:0
remoteapplicationmode:i:1
remoteapplicationname:s:{applicationName}
remoteapplicationprogram:s:{applicationProgram}
remoteapplicationcmdline:s:{applicationCmdline}
disableremoteappcapscheck:i:1
alternate shell:s:rdpinit.exe
shell working directory:s:
gatewayhostname:s:
gatewayusagemethod:i:4
gatewaycredentialssource:i:4
gatewayprofileusagemethod:i:0
promptcredentialonce:i:0
use redirection server name:i:0
username:s:{username}
password 51:b:{passwordHash}
drivestoredirect:s:
EnableCredSSPSupport:i:0
'''

RDP_IMPORT_CERTIFICATE_TEMPLATE = r'''Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\{containerAddress}]
"CertHash"=hex:{containerHash}
"UsernameHint"="{containerServer}\\{username}"

[HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\LocalDevices]
"{containerAddress}"=dword:0000004c
'''

RDP_CLEANUP_CERTIFICATE_TEMPLATE = r'''Windows Registry Editor Version 5.00

[-HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\{containerAddress}]

[HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\LocalDevices]
"{containerAddress}"=-
'''

def _get_http_connection(options):

    class PeerClientResponse(httplib.HTTPResponse, object):
        @property
        def json(self):
            if not hasattr(self, '_json'):
                self._json = json.loads(self.read())
            return self._json

    class PeerClientHTTPConnection(httplib.HTTPConnection, object):
        response_class = PeerClientResponse

        def request(self, method, url, body=None, headers=None):
            if headers is None:
                headers = {}

            if method in ('POST', 'PUT', 'PATCH', 'DELETE') \
               and isinstance(body, dict):
                headers = {k.lower(): v for k, v in headers.items()}
                if 'content-type' not in headers:
                    headers['content-type'] = 'application/json'
                    headers['accept'] = 'application/json'
                body = json.dumps(body)
            return super(PeerClientHTTPConnection, self) \
                .request(method, url, body=body, headers=headers)

    return PeerClientHTTPConnection(options['host'], options['port'])

def get_http_connection():
    return _get_http_connection(OPTIONS)

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

def parse_args_connect_container(argv):
    try:
        opts, args = getopt(argv, 'h', ['help'])
    except GetoptError as ex:
        connect_container_usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            connect_container_usage()

    return args

def connect_container(argv):
    from platform import platform
    import binascii

    argv = parse_args_connect_container(argv)
    if len(argv) != 1:
        connect_container_usage()

    if not platform().lower().startswith('windows'):
        sys.stderr.write('''only work on windows now!
''')
        sys.exit(255)

    try:
        from win32crypt import CryptProtectData
    except ImportError as ex:
        sys.stderr.write('''require package: pywin32
''')
        sys.exit(255)

    container_id = argv[0]

    conn = get_http_connection()
    conn.request('GET', '/v1/containers/%s?embedded={"application":1}' % container_id)
    res = conn.getresponse()

    container = res.json

    metadata = container['connection']['metadata']
    if metadata and metadata['sha1hash'] and metadata['server']:
        sha1hash = metadata['sha1hash']
        server = metadata['server']

        containerHash = ','.join(map(lambda x, y: x+y, sha1hash[::2], sha1hash[1::2]))

        reg_string = RDP_IMPORT_CERTIFICATE_TEMPLATE.format(
            containerAddress=container['connection']['host'],
            containerHash=containerHash,
            containerServer=server,
            username=container['connection']['username'])

        reg_file_name = tempfile.mktemp(suffix='.reg')
        try:
            with open(reg_file_name, 'w') as reg_file:
                reg_file.write(reg_string)
            os.system('regedit /s /q %s' % reg_file_name)
        finally:
            os.path.exists(reg_file_name) and os.unlink(reg_file_name)


    container_password_hash = binascii.hexlify(CryptProtectData(unicode(container['connection']['password']), u'psw', None, None, None, 0))
    rdp_string = RDP_CONNECTION_TEMPLATE.format(
        address=container['connection']['host'],
        applicationName=container['application']['name'],
        applicationProgram=container['application']['program'],
        applicationCmdline=container['application']['cmdline'],
        username=container['connection']['username'],
        passwordHash=container_password_hash)

    rdp_file_name = tempfile.mktemp(suffix='.rdp')
    try:
        with open(rdp_file_name, 'w') as rdp_file:
            rdp_file.write(rdp_string)
        os.system('mstsc ' + rdp_file_name)
    finally:
        os.path.exists(rdp_file_name) and os.unlink(rdp_file_name)

    ## disable cleanup registry now.
    # reg_string = RDP_CLEANUP_CERTIFICATE_TEMPLATE.format(
    #     containerAddress=container['connection']['host'])

    # reg_file_name = tempfile.mktemp(suffix='.reg')
    # try:
    #     with open(reg_file_name, 'w') as reg_file:
    #         reg_file.write(reg_string)
    #     os.system('regedit /s /q ' + reg_file_name)
    # finally:
    #     os.path.exists(rdp_file_name) and os.unlink(reg_file_name)

def connect_container_usage():
    sys.stdout.write('''Usage: %s [...] connect [OPTIONS] <container>

Connect to container

[WARNING] ONLY WORK ON WINDOWS NOW!

Options:
    -h, --help                    print usage

Arguments:
    container                     container id  [require]

''' % sys.argv[0])
    sys.exit(1)

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
        'container': {'autoremove': autoremove}
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
        opts, args = getopt(argv, 'hr', ['help', 'autoremove'])
    except GetoptError as ex:
        run_container_usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            run_container_usage()
        elif k in ('-n', '--name'):
            OPTIONS['name'] = v
        elif k in ('-r', '--autoremove'):
            OPTIONS['autoremove'] = True

    return args

def run_container_usage():
    sys.stdout.write('''Usage: %s [...] run [OPTIONS] <application>

Create a new container from application and start it

Options:
    -h, --help                    print usage
    -n, --name=<random>           container name
    -r, --autoremove=false        auto remove when stop container

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

    {'applications': ps_applications,
     'connect': connect_container,
     'commit': commit_container,
     'start': start_container,
     'stop': stop_container,
     'run': run_container,
     'rm': rm_container,
     'ps': ps_containers,
    }.get(action, lambda *args, **kwargs: usage())(args[1:])
