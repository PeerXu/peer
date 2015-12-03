from flask import request

from peer.server.main import get_app
from peer.server.utils import ParsedRequest

URI = 'rm'
NAME = 'action|container|rm'
METHODS = ['POST']


def parse_request():
    body = request.json
    r = ParsedRequest()
    r.args = {
        'container': {
            '_id': body['container']['_id']
        }
    }
    return r


def rm_container():
    req = parse_request()

    container_id = req.args['container']['_id']

    cli = get_app().get_client()

    res = cli.get('/v1/containers/%s' % container_id)
    _etag = res.json['_etag']

    res = cli.delete('/v1/containers/%s' % container_id,
                     headers={'If-Match': _etag})

    return '', 204


ACTION = rm_container
