from peer.server.graph import core
from peer.server.common import config


_graphs = {}


def load(name='application'):
    global _graphs
    if name in _graphs:
        return _graphs[name]
    cfg = config.load()
    gp = cfg.get('{0}_image_home'.format(name), None)
    if gp is None:
        raise ValueError('load {0} graph failed'.format(name))
    _graphs[name] = core.Graph(gp)
    return _graphs[name]
