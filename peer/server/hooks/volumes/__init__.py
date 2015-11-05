from peer.server.main import get_app

from peer.server.common.volume import load_volume_driver

def on_inserted_volumes(volumes):
    app = get_app()
    cli = app.get_client()

    for volume in volumes:
        res = cli.get('/v1/volumes/%s' % str(volume['_id']))
        volume = res.json

        volume_id = volume['_id']
        volume_uri = volume['uri']
        protocol = volume_uri.split('://')[0]

        drv = load_volume_driver(protocol)
        volume_path = drv.create(volume)

        _etag = res.json['_etag']
        cli.patch('/v1/volumes/%s' % volume_id,
                  headers={'If-Match': _etag},
                  data={'uri': volume_uri + volume_path})

        app.logger.info('create volume: %s' % volume_id)

def on_deleted_item_volumes(volume):
    cli = get_app().get_client()

    volume_id = volume['_id']
    volume_uri = volume['uri']

    protocol = volume_uri.split('://')[0]
    drv = load_volume_driver(protocol)
    drv.delete(volume)

def load_hook(app):
    app.on_inserted_volumes += on_inserted_volumes
    app.on_deleted_item_volumes += on_deleted_item_volumes
    return app
