from peer.server.plugin.action import load_action_plugins

def load_plugins(app):
    load_action_plugins(app)

    return app
