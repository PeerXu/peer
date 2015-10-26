from peer.server.plugin.action import commit
from peer.server.plugin.action import run
from peer.server.plugin.action import rm
from peer.server.plugin.action import stop
from peer.server.plugin.action import start
from peer.server.plugin.action import build

plugins = [
    commit,
    run,
    rm,
    stop,
    start,
    build
]

plugin_prefix = 'action'

def load_action_plugins(app):
    prefix_path = '/'
    if app.config['API_VERSION']:
        prefix_path += '/'.join([app.config['API_VERSION'], plugin_prefix])
    else:
        prefix_path += plugin_prefix

    for plugin in plugins:
        path = '/'.join([prefix_path, plugin.URI])
        view_name = plugin.NAME
        view_func = plugin.ACTION
        methods = plugin.METHODS
        app.add_url_rule(path, view_name, view_func, methods=methods)

    return app
