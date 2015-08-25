from flask import request

URI = 'build'
METHODS = ['POST']

def parse_request():
    body = request.json
    return {
        'application': {
            'name': body['application']['name'],
            'parent': body['application']['parent']
            'peerfile': body['application']['peerfile']
        },
    }

def build_application():
    pass
