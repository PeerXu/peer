from peer.server.utils import REGEX_SHA1
SCHEMA = {
    'applications': {
        'resoucre_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
        'item_url': REGEX_SHA1,
        'schema': {
            '_id': {
                'type': 'sha256'
            },
            'registry': {
                'type': 'string',
                'default': ''
            },
            'namespace': {
                'type': 'string',
                'default': 'library'
            },
            'repository': {
                'type': 'string',
                'required': True
            },
            'tag': {
                'type': 'string',
                'default': ''
            },
            'config': {
                'type': 'dict',
                'schema': {
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
                    'username': {
                        'type': 'string',
                        'default': None,
                        'nullable': True
                    },
                    'password': {
                        'type': 'string',
                        'default': None,
                        'nullable': True
                    }
                }
            },
            'from': {
                'type': 'sha256',
                'data_relation': {
                    'resource': 'applications',
                    'field': '_id',
                    'embeddable': True
                },
                'nullable': True,
                'default': None
            },
            'created': {
                'type': 'datetime',
                'default': None
            },
            'architecture': {
                'type': 'string',
                'default': 'amd64'
            },
            'os': {
                'type': 'string',
                'default': 'windows'
            },
            'os_version': {
                'type': 'string',
                'default': 'windows 7'
            }
        }
    }
}
