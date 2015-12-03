from flask import request

from peer.server.main import get_app
from peer.server.common.agent import PeerAgent
from peer.server.common import task

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
    app = get_app()
    cli = app.get_client()

    # 1. CREATE NEW CONTAINER FOR BUILD APPLICATION

    container_id = request['container']['_id']
    steps = request['container'].get('steps', [])

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'running':
            break
        task.sleep(1)

    # 2. RUN SCRIPTS TO BUILD APPLICATION

    _conn = res.json['connection']
    container_address = _conn['host']
    container_username = _conn['username']
    container_password = _conn['password']
    for step in steps:
        agt = PeerAgent.builder(container_address=container_address,
                                container_username=container_username,
                                container_password=container_password)
        shell, script = step
        fn = 'run_%s' % shell
        assert hasattr(agt, fn)
        res = getattr(agt, fn)(script)
        app.logger.info('[%s] %s', shell.upper(), script)
        if res['status_code']:
            app.logger.error('\n  > '.join([''] + res['std_err'].split('\n')))
            return
        app.logger.info('\n > '.join([''] + res['std_out'].split('\n')))

    agt = PeerAgent.builder(container_address=container_address,
                            container_username=container_username,
                            container_password=container_password)

    # 3. COMMIT CONTAINER TO APPLICATION

    # TODO(Peer): implement graceful shutdown on stop action
    agt.shutdown()
    while True:
        agt = PeerAgent.builder(container_id=container_id)
        if not agt.is_alive():
            break
        task.sleep(1)

    res = cli.post('/v1/action/stop', data={'container': {'_id': container_id}})

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'stop':
            break
        task.sleep(1)

    res = cli.post(
        '/v1/action/commit',
        data={'container': {'_id': container_id},
              'application': {'name': request['application']['name'],
                              'program': request['application']['program'],
                              'cmdline': request['application']['cmdline']}})

    while True:
        res = cli.get('/v1/containers/%s' % container_id)
        if res.json['status'] == 'stop':
            break
        task.sleep(1)

    if request['container']['autoremove']:
        res = cli.post(
            '/v1/action/rm',
            data={'container': {'_id': container_id}})


def build_application():
    req = parse_request()
    cli = get_app().get_client()
    res = cli.post('/v1/action/run', data={'application': {'_id': req['application']['from']}})
    container_id = res.json['_id']
    req['container']['_id'] = container_id
    # TODO(Peer): progress bar for building.
    task.spawn(build_application_callback, req)
    return cli.get('/v1/containers/%s' % container_id)


ACTION = build_application
