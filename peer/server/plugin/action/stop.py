from flask import request

from peer.server.main import get_app
from peer.server.utils import ParsedRequest


URI = 'stop'
NAME = 'action|container|stop'
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

def stop_container():
    req = parse_request()

    container_id = req.args['container']['_id']

    cli = get_app().get_client()

    res = cli.get('/v1/containers/%s' % container_id)
    _etag = res.json['_etag']

    res = cli.patch('/v1/containers/%s' % container_id,
                    headers={'If-Match': _etag},
                    data={'status': 'shutting'})

    return cli.get('/v1/containers/%s' % container_id)

ACTION = stop_container
