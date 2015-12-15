import os
import hashlib


def custom_resource_id(resource, request):
    if 'id' in request.json:
        request.json['_id'] = request.json['id']
        return

    if '_id' not in request.json:
        sha256 = hashlib.sha256()
        sha256.update(os.urandom(256))
        id = sha256.hexdigest()
        request.json['_id'] = id


def load_hook(app):
    app.on_pre_POST += custom_resource_id

    return app
