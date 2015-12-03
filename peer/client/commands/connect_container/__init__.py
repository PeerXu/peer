import os
import sys
from getopt import getopt
from getopt import GetoptError

import tempfile
from peer.client.main import get_http_connection


class RemoteApp(object):

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
full address:s:{host}
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

    RDP_IMPORT_CERTIFICATE_HASH_TEMPLATE = r'''Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\{containerHost}]
"CertHash"=hex:{containerHash}
"UsernameHint"="{containerServer}\\{username}"

[HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\LocalDevices]
"{containerHost}"=dword:0000004c
'''

    RDP_CLEANUP_CERTIFICATE_HASH_TEMPLATE = r'''Windows Registry Editor Version 5.00

[-HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\{containerHost}]

[HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\LocalDevices]
"{containerHost}"=-
'''

    def __init__(self, host, username, password):
        import binascii
        from win32crypt import CryptProtectData

        self.host = host
        self.username = username
        self.password = password
        self.password_hash = binascii.hexlify(
            CryptProtectData(unicode(password), u'psw', None, None, None, 0))

    def _safe_unlink(self, fn):
        os.path.exists(fn) and os.unlink(fn)

    def _import_certificate_hash(self, server, certificate_hash):
        reg_str = self.RDP_IMPORT_CERTIFICATE_HASH_TEMPLATE.format(
            containerHost=self.host,
            containerHash=certificate_hash,
            containerServer=server,
            username=self.username)

        reg_fn = tempfile.mktemp(suffix='.reg')
        try:
            with open(reg_fn, 'w') as reg_f:
                reg_f.write(reg_str)
            os.system('regedit /s /q %s' % reg_fn)
        finally:
            self._safe_unlink(reg_fn)

    def _cleanup_certificate_hash(self):
        reg_str = self.RDP_CLEANUP_CERTIFICATE_HASH_TEMPLATE.format(
            containerHost=self.host)

        reg_fn = tempfile.mktemp(suffix='.reg')
        try:
            with open(reg_fn, 'w') as reg_f:
                reg_f.write(reg_str)
            os.system('register /s /q %s' % reg_fn)
        finally:
            self._safe_unlink(reg_fn)

    def run(self, name, program, cmdline=''):
        rdp_str = self.RDP_CONNECTION_TEMPLATE.format(
            host=self.host,
            applicationName=name,
            applicationProgram=program,
            applicationCmdline=cmdline,
            username=self.username,
            passwordHash=self.password_hash)

        rdp_fn = tempfile.mktemp(suffix='.rdp')
        try:
            with open(rdp_fn, 'w') as rdp_f:
                rdp_f.write(rdp_str)
            os.system('mstsc ' + rdp_fn)
        finally:
            self._safe_unlink(rdp_fn)

    @classmethod
    def simple_run(cls, host, username, password,
                   app_name, app_program, app_cmdline,
                   server=None, certificate_hash=None):
        ra = cls(host, username, password)
        if server and certificate_hash:
            ra._import_certificate_hash(server, certificate_hash)
        ra.run(app_name, app_program, app_cmdline)


def usage():
    sys.stdout.write('''Usage: %s [...] connect [OPTIONS] <container>

Connect to container

[WARNING] ONLY WORK ON WINDOWS NOW!

Options:
    -h, --help                    print usage

Arguments:
    container                     container id  [require]

''' % sys.argv[0])
    sys.exit(1)


def parse_args(argv):
    try:
        opts, args = getopt(argv, 'h', ['help'])
    except GetoptError as ex:
        connect_container_usage()

    for k, v in opts:
        if k in ('-h', '--help'):
            usage()

    return args

def connect_container(argv):
    from platform import platform

    argv = parse_args(argv)
    if len(argv) != 1:
        usage()

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
        container_hash = ','.join(map(lambda x, y: x+y, sha1hash[::2], sha1hash[1::2]))
    else:
        server = None
        container_hash = None

    connection = container['connection']
    host = connection['host']
    username = connection['username']
    password = connection['password']

    # Invoke Startup Script
    RemoteApp.simple_run(
        host, username, password,
        'StartupScript',  # Application Name
        'C:\\\\Users\\\\Public\\\\PeerAgent\\\\startup.bat',  # Application Program
        '',  # Application Cmdline
        server, container_hash)

    # Connection to Application
    application = container['application']
    RemoteApp.simple_run(
        host, username, password,
        application['name'], application['program'], application['cmdline'])


NAME = 'connect'
COMMAND = connect_container
