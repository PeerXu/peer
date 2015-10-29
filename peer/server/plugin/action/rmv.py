from flask import request

from peer.server.main import get_app
from peer.server.utils import ParsedRequest

from peer.server.common.volume.driver.loader import load_volume_drivers

URI = 'rmv'
NAME = 'action|volume|rmv'
METHODS = ['POST']

def parse_request():
    body = request.json

    r = ParsedRequest()
    r.args = {
        'volume': {
            '_id': body['volume']['_id']
        }
    }
    return r

def rm_volume():
    req = parse_request()

    volume_id = req.args['volume']['_id']

    cli = get_app().get_client()

    res = cli.get('/v1/volumes/%s' % volume_id)
    _etag = res.json['_etag']

    res = cli.delete('/v1/volumes/%s' % volume_id, headers={'If-Match': _etag})
    return res

ACTION = rm_volume
