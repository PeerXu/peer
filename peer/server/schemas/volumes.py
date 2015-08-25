from peer.server.utils import REGEX_SHA1

SCHEMA = {
    'volumes': {
        'resoucre_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
        'item_url': REGEX_SHA1,
        'schema': {
            '_id': {
                'type': 'sha1'
            },
            'name': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 16,
                'required': True,
                'unique': True
            },
            'uri': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 512,
                'required': True
            }
        }
    }
}
