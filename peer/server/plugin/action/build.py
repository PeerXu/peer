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
            'parent': body['application']['parent'],
            'min_core': body['application'].get('min_core', 1),
            'min_mem': body['application'].get('min_mem', 512),
        },
        'container': {
            'steps': body.get('container', {}).get('steps', []),
            'autoremove': body.get('container', {}).get('autoremove', True)
        }
    }

def build_application_callback(container_id, application, steps=None):
    if steps is None:
        steps = []

    cli = get_app().get_client()

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'running':
            break
        gevent.sleep(1)

    conn = open_libvirt_connection()
    dom = conn.lookupByName(container_id)
    for step in steps:
        try:
            res = libvirt_qemu.qemuAgentCommand(dom, '{"execute": "guest-peer-agent-execute", "arguments": {"options": "terminal,#base64,%s"}}' % base64.encodestring(step), 30, 0)
            sys.stdout.write('''execute: %s
->
%s
''' % (step, res.json['return']))
            sys.stdout.flush()
        except Exception as ex:
            sys.stderr.write('Build application failed!\n')
            return

    dom.shutdown()

    dom.close()
    conn.close()

    res = cli.post('/v1/action/stop', data={'container': {'_id': container_id}})

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'stop':
            break
        gevent.sleep(1)


def build_application():
    req = parse_request()

    cli = get_app().get_client()

    res = cli.post('/v1/cation/run',
                   data={
                       'application': {'_id': req['application']['parent']},
                       'container': {'autoremove': req['container']['autoremove']}
                   })

    container_id = res.json['_id']
    return cli.get('/v1/containers/%s' % container_id)

ACTION = build_application
