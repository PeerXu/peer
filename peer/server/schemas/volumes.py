from peer.server.utils import REGEX_SHA1

SCHEMA = {
    'volumes': {
        'additional_lookup': {
            'url': REGEX_SHA1,
            'field': '_id'
        },
        'schema': {
            '_id': {
                'type': 'sha256'
            },
            'name': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 64,
                'required': True,
                'unique': True
            },
            'uri': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 512,
                'required': True
            },
            'metadata': {
                'type': 'dict',
                'default': {}
            }
        }
    }
}
