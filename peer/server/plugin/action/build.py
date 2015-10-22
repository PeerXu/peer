import sys
import gevent
import libvirt_qemu
from flask import request

from peer.server.main import get_app
from peer.server.utils import open_libvirt_connection

URI = 'build'
NAME = 'action|application|build'
METHODS = ['POST']

def parse_request():
    body = request.json
    return {
        'application': {
            'name': body['application']['name'],
            'program': body['application']['program'],
            'cmdline': body['application']['cmdline'],
            'from': body['application']['from'],
            'min_core': body['application'].get('min_core', 1),
            'min_mem': body['application'].get('min_mem', 512),
        },
        'container': {
            'steps': body.get('container', {}).get('steps', []),
            'autoremove': body.get('container', {}).get('autoremove', True)
        }
    }

def build_application_callback(request):
# def build_application_callback(container_id, application, steps=None):
    container_id = request['container']['id']
    steps = request['container'].get('steps', [])

    cli = get_app().get_client()

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'running':
            break
        gevent.sleep(1)

    # TODO(Peer): execute steps.

    res = cli.post('/v1/action/stop', data={'container': {'_id': container_id}})

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'stop':
            break
        gevent.sleep(1)


def build_application():
    req = parse_request()
    cli = get_app().get_client()
    res = cli.post('/v1/cation/run', data={'application': {'_id': req['application']['from']}})
    container_id = res.json['_id']
    req['container']['id'] = container_id
    gevent.spawn(build_application_callback, req)
    return cli.get('/v1/containers/%s' % container_id)

ACTION = build_application
