from peer.server.hooks import containers
from peer.server.hooks import applications
from peer.server.hooks import volumes
from peer.server.hooks import plugins

__MODULES__ = [containers, applications, volumes, plugins]

def load_hooks(app):
    map(lambda m: m.load_hook(app), __MODULES__)
    return app
