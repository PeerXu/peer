_config = None


def load():
    global _config
    if _config is not None:
        return _config

    from peer.common import config
    cfg = config.load()
    conf = {
        'host': '127.0.0.1'
    }
    conf.update(cfg._config)
    _config = config.Config(conf)
    return _config
