from flask import request

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
        'repository': {
            'registry': body['application']['registry'],
            'namespace': body['application']['namespace'],
            'repository': body['application']['repository'],
            'tag': body['application']['tag']
        }
    }

    return r


def _mix_repo_tag(repo, tag):
    return {
        '_id': tag['layer_id'],
        'namespace': repo['namespace'],
        'repository': repo['repository'],
        'tag': tag['name'],
        'program': repo['program'],
        'cmdline': repo['cmdline'],
        'min_core': repo['min_core'],
        'min_mem': repo['min_mem'],
    }


def _pull_repository(repo):
    namespace = repo['namespace']
    repository = repo['repository']
    asked_tag = repo['tag']
    r = registry.new_registry(repo['registry'])
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


def _pull_application(r, app_id):
    grp = graph.load()
    apps = r.get_remote_history(app_id)

    for app in apps:
        app_json = r.get_remote_app_json(app_id)
        app_checksum = r.get_remote_app_checksum(app_id)
        app_compressed_layer = r.get_remote_app_compressed_layer(app_id)
        grp.register_application(app_json, app_checksum, app_compressed_layer)


def pull_application():
    req = parse_request()
    success = _pull_repository(req.args['repository'])
    return PeerResponse('', 204 if success else 400)


ACTION = pull_application
