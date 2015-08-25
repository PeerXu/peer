from operator import add

def load_validator():
    from peer.server.validators import containers
    from peer.server.validators import plugins

    validators = tuple(reduce(add, [containers.VALIDATORS,
                                    plugins.VALIDATORS], []))

    return type('PeerValidator', validators, {})
