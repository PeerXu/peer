import time
import gevent
from peer.server.common.agent.driver.loader import load_agent_drivers

DRIVERS = load_agent_drivers()

class PeerAgent(object):
    '''run_cmd, run_ps method should wraped by agent drivers.
    '''

    def __init__(self):
        # required
        self.container_id = None
        self.container_address = None
        self.container_username = None
        self.container_password = None
        self.timeout = 300
        self.interval = 10

    @classmethod
    def builder(cls, container_id=None, container_address=None,
                container_username=None, container_password=None):
        self = cls()
        self.container_id = container_id
        self.container_address = container_address
        self.container_username = container_username
        self.container_password = container_password
        return self

    @DRIVERS.QemuGuestAgentDriver
    def get_local_address(self):
        start_at = time.time()
        while True:
            try:
                if time.time() - start_at > self.timeout:
                    return None
                addr = self._get_local_address()
                if addr.startswith('127.0.0') or addr.startswith('169'):
                    raise
                return addr
            except Exception as ex:
                gevent.sleep(self.interval)

    @DRIVERS.QemuGuestAgentDriver
    def is_alive(self):
        return self._is_alive()

    @DRIVERS.WinRMAgentDriver
    def get_rdp_info(self):
        resp = self._run_ps('Get-WmiObject -namespace root/cimv2/terminalservices -class "Win32_TSGeneralSetting"')

        if resp['status_code']:
            raise Exception('get rdp hash failed, %s' % resp['std_err'])

        dat = resp['std_out']
        lines = []
        cache_line = ''
        for line in dat.split('\n'):
            if line.startswith(' ' * 10):
                line = line.strip()
                cache_line += line
            else:
                line = line.strip()
                lines.append(cache_line)
                cache_line = line

        o = {}
        for line in lines:
            if line == '':
                if o and 'RDP' in o.get('__RELPATH', ''):
                    return {'server': o['__SERVER'],
                            'sha1hash': o['SSLCertificateSHA1Hash']}
                o = {}
            else:
                try:
                    k, v = line.split(':', 1)
                    o[k.strip()] = v.strip()
                except:
                    pass

        return {'server': None, 'sha1hash': None}

    @DRIVERS.WinRMAgentDriver
    def shutdown(self, delay=0):
        return self._run_cmd("shutdown -s -t %s" % delay)

    @DRIVERS.WinRMAgentDriver
    def run_cmd(self, script):
        return self._run_cmd(script)

    @DRIVERS.WinRMAgentDriver
    def run_ps(self, script):
        return self._run_ps(script)
