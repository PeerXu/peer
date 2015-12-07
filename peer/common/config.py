import re


class Config(object):
    RENDER_REGEX = re.compile(r'{{\s?[^\s]+\s?}}')
    RENDER_KEY_REGEX = re.compile(r'{{\s?([^\s]+)\s?}}')

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
            return self.get(key)

    def get(self, *args, **kwargs):
        return self._render_value(self._config.get(*args, **kwargs))

    def set(self, key, value):
        self._config[key] = value

    def __contains__(self, key):
        return key in self._config

    def _render_value(self, v):
        # prepare render keys
        prks = self.RENDER_REGEX.findall(v)
        if not prepare_render_keys:
            return v

        # rendered value
        rv = v
        for prk in prks:
            k = self.RENDER_KEY_REGEX.findall(prk)[0]
            rv = rv.replace(prk, self._rander_value(self.get(k)))

        return rv


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
