_config = None


def load():
    global _config
    if _config is not None:
        return _config

    from peer.common import config
    cfg = config.load()
    conf = {
        'host': '0.0.0.0',
        'peer_home': '/home/cloud/peer',
        'container_home': '/home/cloud/peer/containers',
        'container_image_home': '/home/cloud/peer/containers/images',
        'application_home': '/home/cloud/peer/applications',
        'application_image_home': '/home/cloud/peer/applications/images',
        'volume_home': '/volumes',
        'volume_nfs_host': '10.12.31.1'
    }
    conf.update(cfg._config)
    _config = config.Config(conf)
    return _config
