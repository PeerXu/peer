from peer.server.utils import REGEX_SHA1

SCHEMA = {
    'containers': {
        'resoucre_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
        'item_url': REGEX_SHA1,
        'schema': {
            '_id': {
                'type': 'sha1'
            },
            'name': {
                'type': 'string',
                'required': True,
                'unique': True,
            },
            'type': {
                'type': 'string',
                'default': 'kvm',
                'allowed': ['kvm']
            },
            'connection': {
                'type': 'dict',
                'schema': {
                    'protocol': {
                        'type': 'string',
                        'default': 'rdp',
                        'allowed': ['rdp'],
                    },
                    'host': {
                        'type': 'string',
                        'default': None,
                        'nullable': True
                    },
                    'port': {
                        'type': 'integer',
                        'default': None,
                        'nullable': True
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
                    },
                    'metadata': {
                        'type': 'dict',
                        'default': {},
                    }
                }
            },
            'status': {
                'type': 'string',
                'is_container_status_updatable': True,
                'default': 'creating',
                'allowed': ['creating', 'stop', 'booting', 'starting', 'running', 'connecting', 'connected', 'disconnecting', 'shutting', 'commiting', 'error'],
            },
            'application': {
                'type': 'sha1',
                'data_relation': {
                    'resource': 'applications',
                    'field': '_id',
                    'embeddable': True
                },
                'required': True
            },
            'volumes': {
                'type': 'list',
                'schema': {
                    'type': 'sha1',
                    'data_relation': {
                        'resource': 'volumes',
                        'field': '_id',
                        'embeddable': True
                    }
                },
                'default': []
            },
            'autoremove': {
                'type': 'boolean',
                'default': False
            }
        }
    }
}
