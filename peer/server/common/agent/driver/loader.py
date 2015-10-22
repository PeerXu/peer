_DRIVER = None

class Driver(object): pass

def load_agent_drivers():
    global _DRIVER

    if _DRIVER is None:
        from os import walk
        from peer.server.common.agent import driver
        from importlib import import_module

        _DRIVER = Driver()

        path = driver.__path__[0]
        _, dirs, files = walk(path).next()

        modules = dirs + [f.rsplit('.', 1)[0] for f in files if f.endswith('.py')]
        for module in modules:
            try:
                m = import_module('peer.server.common.agent.driver.%s' % module)
                if hasattr(m, 'DRIVER'):
                    setattr(_DRIVER, m.DRIVER.NAME, m.DRIVER())
            except Exception as ex:
                pass

    return _DRIVER
