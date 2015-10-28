from flask import request

from peer.server.main import get_app
from peer.server.utils import ParsedRequest
from peer.common.utils import random_name
from peer.server.common import task

from peer.server.common.volume.driver.loader import load_volume_drivers

URI = 'cv'
NAME = 'action|volume|cv'
METHODS = ['POST']

def parse_request():
    body = request.json

    r = ParsedRequest()
    r.args = {
        'volume': {
            'name': body['volume'].get('name', random_name()),
            'type': body['volume']['type']
        }
    }
    return r

def _create_volume_callback(volume_id):
    volume_drivers = load_volume_drivers()

    app = get_app()
    cli = app.get_client()

    res = cli.get('/v1/volumes/%s' % volume_id)
    volume = res.json
    volume_id = volume['_id']
    volume_uri = volume['uri']
    protocol = volume_uri.split('://')[0]

    if protocol not in volume_drivers:
        app.logger.error('error volume protocol')
        return

    drv = volume_drivers[protocol]()
    volume_path = drv.create(volume)

    _etag = res.json['_etag']
    cli.patch('/v1/volumes/%s' % volume_id,
              headers={'If-Match': _etag},
              data={'uri': volume_uri + volume_path})

    app.logger.info('create volume: %s' % volume_id)

def create_volume():
    req = parse_request()

    cli = get_app().get_client()

    body = {
        'name': req.args['volume']['name'],
        'uri': req.args['volume']['type'] + '://'
    }
    res = cli.post('/v1/volumes', headers=[('Content-type', 'application/json')], data=body)

    volume_id = res.json['_id']
    task.spawn(_create_volume_callback, volume_id)

    return cli.get('/v1/volumes/%s' % volume_id)

ACTION = create_volume
