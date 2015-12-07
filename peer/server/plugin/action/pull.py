from flask import request

from peer.server.main import get_app
from peer.server.utils import PeerResponse
from peer.server.utils import ParsedRequest
from peer.server import graph
from peer.server import registry


URI = 'pull'
NAME = 'action|application|pull'
METHODS = ['POST']


def parse_request():
    body = request.json

    r = ParsedRequest()
    r.args = {
        'application': {
            'registry': body['application']['registry'],
            'namespace': body['application']['namespace'],
            'repository': body['application']['repository'],
            'tag': body['application']['tag']
        }
    }

    return r


def _pull_repository(repo_info):
    namespace = repo_info['namespace']
    repository = repo_info['repository']
    asked_tag = repo_info['tag']
    r = registry.new_registry(repo_info['registry'])
    # TODO(Peer): ignore repository data.
    # repo_data = r.get_repository_data(namespace, repository)
    tags = r.get_remote_tags(namespace, repository)

    success = False
    if asked_tag:
        for tag in tags:
            if asked_tag == tag['name']:
                _pull_application(r, tag['application_id'])
                success = True
                break
    else:
        for tag in tags:
            _pull_application(r, tag['application_id'])
        success = True

    return success


def _create_application(app_json):
    cli = get_app().get_client()

    res = cli.post('/v1/applications', data=app_json)
    return res.status == 200


def _pull_application(r, app_id):
    grp = graph.load()
    apps = r.get_remote_history(app_id)

    for img in apps:
        img_json = r.get_remote_app_json(app_id)
        img_checksum = r.get_remote_app_checksum(app_id)
        img_compressed_layer = r.get_remote_app_compressed_layer(app_id)
        _create_application(img_json)
        grp.registerApplication(img_json, img_checksum, img_compressed_layer)


def pull_application():
    req = parse_request()

    success = _pull_repository(req.args['application'])

    return PeerResponse('', 204 if success else 400)


ACTION = pull_application
