# import os
# from peer.server.common import config
# cfg = config.load()


# def on_inserted_applications(items):
#     for application in items:
#         base = ' -b %s.qcow2 ' % application['from'] if application['from'] else ''
#         img = os.path.join(cfg.application_image_home, '%s.qcow2' % application['_id'])
#         cmd = 'qemu-img create -f qcow2 %s %s 500G' % (base, img)
#         os.system(cmd)


# def on_deleted_item_applications(application):
#     img = os.path.join(cfg.application_image_home, '%s.qcow2' % application['_id'])
#     cmd = 'rm -v %s' % img
#     os.system(cmd)


def load_hook(app):
    # app.on_inserted_applications += on_inserted_applications
    # app.on_deleted_item_applications += on_deleted_item_applications
    return app
