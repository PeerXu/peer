from peer.server.utils import REGEX_SHA1
SCHEMA = {
    'users': {
        'additional_lookup': {
            'url': REGEX_SHA1,
            'field': '_id'
        },
        'schema': {
            '_id': {
                'type': 'sha256'
            },
            'email': {
                'type': 'string'
            },
            'password': {
                'type': 'string',
                'minlength': 8
            },
            'name': {
                'type': 'string',
                'maxlength': 32
            }
        }
    }
}
