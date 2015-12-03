import libvirt
from flask.wrappers import Response
from flask.testing import FlaskClient
from flask import json


REGEX_SHA1 = 'regex("[0-9a-f]{40}")'


class PeerResponse(Response):
    default_mimetype = 'application/json'

    @property
    def json(self):
        if not hasattr(self, '_json'):
            setattr(self, '_json', json.loads(self.data))
        if '_etag' in self._json:
            self._json['_etag'] = str(self._json['_etag'])
        return self._json

    @property
    def statusCode(self):
        return self.status_code


class PeerClient(FlaskClient):
    def open(*args, **kwargs):
        is_json = False
        if 'data' in kwargs:
            data = kwargs['data']
            if isinstance(data, dict):
                kwargs['data'] = json.dumps(data)
                is_json = True

        if 'headers' in kwargs:
            headers = kwargs['headers']
            if isinstance(headers, (list, tuple)):
                headers = dict({k.lower(): v for k, v in kwargs['headers']})
            if 'content-type' not in headers:
                headers['content-type'] = 'application/json'
            kwargs['headers'] = headers.items()
        else:
            kwargs['headers'] = [('content-type', 'application/json')]

        return FlaskClient.open(*args, **kwargs)


class ParsedRequest(object):
    args = None


def open_libvirt_connection():
    return libvirt.open('qemu:///system')
