import httplib
from flask import json

from peer.common import config


def random_name():
    return str(__import__('uuid').uuid4()).split('-')[0]


def parse_repository_name(name):
    cfg = config.load()

    name = name.strip('/')
    registry = '%s:%s' % (cfg.registry_host, cfg.registry_port)
    name, tag = name.rsplit(':', 1) if ':' in name else (name, None)
    namespace, repository = name.lsplit('/', 1) if '/' in name else ('library', name)

    return (registry, namespace, repository, tag)


def get_http_connection(cfg):

    class PeerClientResponse(httplib.HTTPResponse, object):
        @property
        def json(self):
            if not hasattr(self, '_json'):
                self._json = json.loads(self.read())
            return self._json

    class PeerClientHTTPConnection(httplib.HTTPConnection, object):
        response_class = PeerClientResponse

        def request(self, method, url, body=None, headers=None):
            if headers is None:
                headers = {}

            if method in ('POST', 'PUT', 'PATCH', 'DELETE') \
               and isinstance(body, dict):
                headers = {k.lower(): v for k, v in headers.items()}
                if 'content-type' not in headers:
                    headers['content-type'] = 'application/json'
                    headers['accept'] = 'application/json'
                body = json.dumps(body)
            return super(PeerClientHTTPConnection, self) \
                .request(method, url, body=body, headers=headers)

    return PeerClientHTTPConnection(cfg.host, cfg.port)
