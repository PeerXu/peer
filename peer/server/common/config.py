_config = None


def load():
    global _config
    if _config is not None:
        return _config

    from peer.common import config
    cfg = config.load()
    config = {
        'peer_home': '/home/cloud/peer',
        'container_home': '/home/cloud/peer/containers',
        'container_image_home': '/home/cloud/peer/containers/images',
        'application_home': '/home/cloud/peer/applications',
        'application_image_home': '/home/cloud/peer/applications/images',
        'volume_home': '/volumes',
        'volume_nfs_host': '10.12.31.1'
    }
    config.update(cfg._config)
    _config = config.Config(config)
    return _config
