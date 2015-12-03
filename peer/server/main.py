from peer.common import config


def make_app():
    from eve import Eve
    from peer.server.schemas import load_schemas
    from peer.server.hooks import load_hooks
    from peer.server.utils import PeerResponse
    from peer.server.utils import PeerClient
    from peer.server.validators import load_validator
    from peer.server.json_encoders import load_json_encoder
    from peer.server.plugin import load_plugins

    settings = {
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': 27017,
        'MONGO_DBNAME': 'peer-test',

        'API_VERSION': 'v1',
        # 'HATEOAS': False,

        'RESOURCE_METHODS': ['GET', 'POST'],
        'ITEM_METHODS': ['GET', 'PATCH', 'PUT', 'DELETE'],

        'DOMAIN': load_schemas()
    }
    app = Eve(settings=settings,
              validator=load_validator(),
              json_encoder=load_json_encoder())
    app.response_class = PeerResponse
    app.test_client_class = PeerClient
    app.get_client = app.test_client
    load_hooks(app)
    load_plugins(app)
    return app


def get_app():
    try:
        from flask import current_app
        current_app._get_current_object()
        return current_app
    except RuntimeError:
        return make_app()


def start_server(host, port):
    app = get_app()
    app.run(host=host, port=port, debug=True)


def main(argv):
    cfg = config.load()
    start_server(host=cfg.host, port=cfg.port)
