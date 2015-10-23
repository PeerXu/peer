import os
import gevent
from subprocess import Popen
from subprocess import PIPE
from flask import request
from flask import json
from flask import current_app

from peer.server.config import get_config
from peer.server.main import get_app
from peer.server.utils import ParsedRequest

CONFIG = get_config()

URI = 'commit'
NAME = 'action|container|commit'
METHODS = ['POST']

def parse_request():
    body = request.json
    r = ParsedRequest()
    r.args = {
        'container': {
            '_id': body['container']['_id']
        },
        'application': {
            'name': body['application']['name'],
            'program': body['application']['program'],
            'cmdline': body['application'].get('cmdline', '')
        }
    }
    return r

def _commit_container_callback(container_id, application_id):
    cli = get_app().get_client()

    application_img = os.path.join(CONFIG['APPLICATION_IMAGE_HOME'], '%s.qcow2' % application_id)
    container_img = os.path.join(CONFIG['CONTAINER_IMAGE_HOME'], '%s.qcow2' % container_id)
    p = Popen(['qemu-img', 'convert', '-f', 'qcow2', '-O', 'qcow2', container_img, application_img], stdout=PIPE)
    while True:
        if p.poll() is not None:
            break
        gevent.sleep(1)

    res = cli.get('/v1/containers/%s' % container_id)
    _etag = res.json['_etag']

    res = cli.patch('/v1/containers/%s' % container_id,
                    headers={'If-Match': _etag},
                    data={'status': 'stop'})

def commit_container():
    req = parse_request()

    container_id = req.args['container']['_id']

    cli = get_app().get_client()
    res = cli.get('/v1/containers/%s?embedded={"application":1}' % container_id)
    _etag = res.json['_etag']

    req.args['application']['from'] = res.json['application']['_id']
    res = cli.post('/v1/applications',
                   data={'name': req.args['application']['name'],
                         'program': req.args['application']['program'],
                         'cmdline': req.args['application']['cmdline'],
                         'from': req.args['application']['from']})

    application_id = res.json['_id']
    cli.patch('/v1/containers/%s' % container_id,
              headers={'If-Match': _etag},
              data={'status': 'commiting'})

    gevent.spawn(_commit_container_callback, container_id, application_id)

    return cli.get('/v1/containers/%s' % container_id)

ACTION = commit_container
