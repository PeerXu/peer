_DRIVER = None

def load_volume_drivers():
    global _DRIVER

    if _DRIVER is None:
        from os import walk
        from peer.server.common.volume import driver
        from importlib import import_module

        _DRIVER = {}

        path = driver.__path__[0]
        _, dirs, files = walk(path).next()

        modules = dirs + [f.rsplit('.', 1)[0] for f in files if f.endswith('.py')]
        for module in modules:
            try:
                m = import_module('peer.server.common.volume.driver.%s' % module)
                if hasattr(m, 'DRIVER'):
                    _DRIVER[m.DRIVER.PROTOCOL] = m.DRIVER
            except Exception as ex:
                pass

    return _DRIVER

def load_volume_driver(protocol):
    return load_volume_drivers()[protocol]()
