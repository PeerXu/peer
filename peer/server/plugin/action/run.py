from flask import request
from flask import json

from peer.server.main import get_app
from peer.server.utils import ParsedRequest
from peer.common.utils import random_name
from peer.server.common import task

URI = 'run'
NAME = 'action|container|run'
METHODS = ['POST']

def parse_request():
    body = request.json
    r = ParsedRequest()
    r.args = {
        'application': {
            '_id': body['application']['_id']
        },
        'container': {
            'name': body.get('container', {}).get('name', random_name()),
            'autoremove': body.get('container', {}).get('autoremove', False),
            'volumes': body.get('container', {}).get('volumes', [])

        }
    }
    return r

def _run_container_callback(container_id):
    cli = get_app().get_client()

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'stop':
            break
        task.sleep(1)

    _etag = res.json['_etag']

    cli.patch('/v1/containers/%s' % container_id,
              headers=[('Content-Type', 'application/json'),
                       ('If-Match', _etag)],
              data=json.dumps({'status': 'booting'}))

def run_container():
    req = parse_request()

    cli = get_app().get_client()

    res = cli.post('/v1/containers',
                   headers=[('Content-Type', 'application/json')],
                   data=json.dumps({'name': req.args['container']['name'],
                                    'application': req.args['application']['_id'],
                                    'autoremove': req.args['container']['autoremove'],
                                    'volumes': req.args['container']['volumes']}))

    container_id = res.json['_id']
    task.spawn(_run_container_callback, container_id)

    return cli.get('/v1/containers/%s' % container_id)

ACTION = run_container
