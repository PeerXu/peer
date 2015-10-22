from peer.server.common.agent.driver._interface import AgentDriverInterface

class WinRMAgentDriver(AgentDriverInterface):
    NAME = 'WinRMAgentDriver'

    def __init__(self):
        super(WinRMAgentDriver, self).__init__()
        self.container_address = None
        self.container_username = None
        self.container_password = None

    def _custom_initialize(self, agent):
        self.container_address = agent.container_address
        self.container_username = agent.container_username
        self.container_password = agent.container_password

    def _run(self, shell, script):
        # NOTE(Peer): can not use `import` statement import `WinRM` module
        winrm = __import__('winrm')
        session = winrm.Session(
            self.container_address,
            auth=(self.container_username, self.container_password))
        assert shell in ('cmd', 'ps')
        fn = getattr(session, 'run_%s' % shell)
        resp = fn(script)
        return {'status_code': resp.status_code,
                'std_out': resp.std_out,
                'std_err': resp.std_err}

    def _run_cmd(self, script):
        return self._run('cmd', script)

    def _run_ps(self, script):
        return self._run('ps', script)

DRIVER = WinRMAgentDriver
