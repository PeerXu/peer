from dateutil.parser import parse as iso8601_to_datetime

from peer.server.common import config
from peer.common.utils import _get_http_connection as get_http_connection


def new_registry(registry):
    return Registry.new_registry(registry)


class Registry(object):
    def __init__(self, registry, version):
        self._registry = registry
        self._version = version

    @classmethod
    def new_registry(cls, registry=None, version='v1'):
        cfg = config.load()
        registry = registry if registry else '{0}:{1}'.format(cfg.registry_host, cfg.registry_port)
        return cls(registry, version)

    def get_http_connection(self):
        cfg = config.load()
        host, port = self._registry.split(':') if ':' in self._registry else (self._registry, cfg.registry_port)
        port = int(port)

        return get_http_connection(host, port)

    def get_repository_data(self, namespace, repository):
        conn = self.get_http_connection()
        conn.request('GET', '/v1/repositories/{0}/{1}/json'.format(namespace, repository))

        res = conn.getresponse()

        if res.status == 404:
            raise ValueError('Repository not found')

        repo = res.json
        return repo

    def get_remote_tags(self, namespace, repository):
        conn = self.get_http_connection()
        conn.request('GET', '/v1/repositories/{0}/{1}/tags'.format(namespace, repository))

        res = conn.getresponse()

        if res.status == 404:
            raise ValueError('Repository not found')

        tags = res.json
        return tags

    def get_remote_history(self, app_id):
        conn = self.get_http_connection()
        conn.request('GET', '/v1/applications/{0}/ancestry'.format(app_id))

        res = conn.getresponse()

        if res.status == 404:
            raise ValueError('Repository not found')

        history = res.json
        return history

    def get_remote_app_json(self, app_id):
        conn = self.get_http_connection()
        conn.request('GET', '/v1/applications/{0}/json'.format(app_id))

        res = conn.getresponse()

        if res.status == 404:
            raise ValueError('Response not found')

        app_json = res.json
        return app_json

    def get_remote_app_checksum(self, app_id):
        conn = self.get_http_connection()
        conn.request('GET', '/v1/applications/{0}/checksum'.format(app_id))

        res = conn.getresponse()

        if res.status == 404:
            raise ValueError('Response not found')

        app_checksum = res.json
        return app_checksum

    def get_remote_app_compressed_layer(self, app_id):
        conn = self.get_http_connection()
        conn.request('GET', '/v1/applications/{0}/layer'.format(app_id))

        res = conn.getresponse()

        if res.status == 404:
            raise ValueError('Response not found')

        app_compressed_layer = res.read()
        return app_compressed_layer

    def application_to_registry_application_json(self, app):
        app_json = dict(app)
        app_json['layer_id'] = app_json.pop('_id')
        app_json['created'] = app_json['created'].isoformat() + 'Z'
        return app_json

    def application_from_registry_application_json(self, app_json):
        app = dict(app_json)
        app['_id'] = app.pop('layer_id')
        app['created'] = iso8601_to_datetime(app['created'])
        return app
