class Config(object):
    def __init__(self, config=None):
        if config is None:
            config = {}

        if isinstance(config, Config):
            config = config._config

        self._config = config

    def __repr__(self):
        return repr(self._config)

    def __getattr__(self, key):
        if key in self._config:
            return self._config[key]

    def get(self, *args, **kwargs):
        return self.config.get(*args, **kwargs)

    def set(self, key, value):
        self._config[key] = value

    def __contains__(self, key):
        return key in self._config


_config = None


def load():
    global _config
    if _config is not None:
        return _config
    _config = Config({
        'port': 11214,
        'registry_host': '127.0.0.1',
        'registry_port': 5000
    })
    return _config
