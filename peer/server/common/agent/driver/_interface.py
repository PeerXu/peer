from functools import wraps

class AgentDriverInterface(object):

    def __call__(self, f):
        @wraps(f)
        def wrapped(_self, *args, **kwargs):
            self.initialize(_self)
            return f(_self, *args, **kwargs)
        return wrapped

    def initialize(self, agent):
        self.agent = agent
        agent._run_cmd = self._run_cmd
        agent._run_ps = self._run_ps
        self._custom_initialize(agent)

    def _custom_initialize(self, agent):
        pass

    def _run_cmd(self, script):
        raise NotImplementedError

    def _run_ps(self, script):
        raise NotImplementedError
