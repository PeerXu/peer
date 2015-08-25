from peer.server.utils import REGEX_SHA1
SCHEMA = {
    'applications': {
        'resoucre_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
        'item_url': 'regex("[0-9a-f]{40}")',
        'schema': {
            '_id': {
                'type': 'sha1'
            },
            'name': {
                'type': 'string',
                'required': True,
                'unique': True
            },
            'program': {
                'type': 'string',
                'default': ''
            },
            'cmdline': {
                'type': 'string',
                'default': ''
            },
            'min_core': {
                'type': 'integer',
                'default': 1
            },
            'min_mem': {
                'type': 'integer',
                'default': 512
            },
            'parent': {
                'type': 'sha1',
                'data_relation': {
                    'resource': 'applications',
                    'field': '_id',
                    'embeddable': True
                },
                'nullable': True,
                'default': None
            }
        }
    }
}
