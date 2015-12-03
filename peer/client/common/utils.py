from peer.common import utils
from peer.client.common import config


def get_http_connection():
    cfg = config.load()
    return utils.get_http_connection(cfg)
