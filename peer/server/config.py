from flask.config import Config as _Config
from peer.server import settings

CONFIG = _Config('.')
CONFIG.from_object(settings)

def get_config():
    return CONFIG
