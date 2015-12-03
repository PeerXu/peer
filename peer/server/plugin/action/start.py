from flask import request

from peer.server.common import config
from peer.server.main import get_app
from peer.server.utils import ParsedRequest

cfg = config.load()

URI = 'start'
NAME = 'action|container|start'
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


def start_container():
    req = parse_request()

    container_id = req.args['container']['_id']

    cli = get_app().get_client()

    res = cli.get('/v1/containers/%s' % container_id)
    _etag = res.json['_etag']

    res = cli.patch('/v1/containers/%s' % container_id,
                    headers={'If-Match': _etag},
                    data={'status': 'booting'})

    return cli.get('/v1/containers/%s' % container_id)


ACTION = start_container
