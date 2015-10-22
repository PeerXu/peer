from functools import wraps

_DRIVER = None
class Driver(object): pass

def _driver_wrapper_helper(driver):
    def wrapper(f):
        @wraps(f)
        def wrapped(_self, *args, **kwargs):
            drv = driver()
            drv.initialize(_self)
            return f(_self, *args, **kwargs)
        return wrapped
    return wrapper

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
                    setattr(_DRIVER, m.DRIVER.NAME, _driver_wrapper_helper(m.DRIVER))
            except Exception as ex:
                pass

    return _DRIVER
