def _get_http_connection(options):

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

    return PeerClientHTTPConnection(options['host'], options['port'])

def get_http_connection():
    from peer.common import options
    return _get_http_connection(options.CLIENT_OPTIONS)
