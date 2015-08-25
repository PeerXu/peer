def custom_resource_id(resource, request):
    from uuid import uuid4
    from sha import sha

    id = sha(str(uuid4())).hexdigest()
    request.json['_id'] = id


def load_hook(app):
    app.on_pre_POST += custom_resource_id

    return app
