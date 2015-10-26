import json
import base64
import libvirt
import libvirt_qemu
from peer.server.utils import open_libvirt_connection
from peer.server.common.agent.driver._interface import AgentDriverInterface

base64_encode = lambda s: base64.encodestring(s).replace("\n", "")
base64_decode = base64.decodestring

class Option(object):
    @classmethod
    def new(cls, func, args):
        self = cls()
        self.function = func
        self.arguments = args
        return self

    def dumps(self):
        return self.function + \
            ",#base64:json," + \
            base64_encode(json.dumps(self.arguments))

class QemuGuestAgentDriver(AgentDriverInterface):
    NAME = 'QemuGuestAgentDriver'

    def __init__(self):
        super(QemuGuestAgentDriver, self).__init__()
        self.container_id = None
        self._conn = None
        self._dom = None

    def close(self):
        self._close_domain()
        self._close_connection()

    def _close_domain(self):
        if self._dom:
            self._dom.close()
            self._dom = None

    def _close_connection(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def connection(self):
        self._open_connection()
        return self._conn

    @property
    def domain(self):
        self._open_domain()
        return self._dom

    def _open_connection(self):
        if not self._conn:
            self._conn = open_libvirt_connection()

    def _open_domain(self):
        if not self._dom:
            assert self.container_id
            self._dom = self.connection.lookupByName(self.container_id)

    def make_request_payload(self, function, arguments=None):
        options = (function + ",#base64:json," + \
                   base64_encode(json.dumps(arguments))) \
                   if arguments is not None else function

        payload = {"execute": "guest-peer-agent-execute",
                   "arguments": {"options": options}}
        return json.dumps(payload)

    def parse_response(self, res):
        if "," in res:
            opts, enc = res.split(",", 1)
            if opts.startswith("#") and ":" in opts:
                fmt, typ = opts.split(":", 1)
                fmt = fmt[1:]
                dec_func = {"base64": base64.decodestring}.get(fmt)
                typ_func = {"str": str,
                            "unicode": unicode,
                            "int": int,
                            "float": float,
                            "json": json.loads}.get(typ)
                if not dec_func:
                    raise Exception("unsupport decoding format: %s" % fmt)
                if not typ_func:
                    raise Exception("unsupport type: %s" % typ)
                return typ_func(dec_func(enc))
            else:
                raise Exception("unsupport format: %s" % res)
        else:
            return res

    def call(self, function, arguments=None, timeout=None):
        res = libvirt_qemu.qemuAgentCommand(
            self.domain, self.make_request_payload(function, arguments), timeout or 30, 0)
        res = json.loads(res)
        return self.parse_response(res['return'])

    def _get_local_address(self):
        return self.call('get-local-address')

    def _custom_initialize(self, agent):
        self.container_id = agent.container_id
        agent._get_local_address = self._get_local_address
        agent._is_alive = self._is_alive

    def _is_alive(self):
        try:
            dom = self.domain
            return dom.info()[0] != libvirt.VIR_DOMAIN_SHUTOFF
        except libvirt.libvirtError as ex:
            return False

DRIVER = QemuGuestAgentDriver
