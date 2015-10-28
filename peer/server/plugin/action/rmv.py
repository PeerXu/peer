from flask import request

from peer.server.main import get_app
from peer.server.utils import ParsedRequest

from peer.server.common.volume.driver.loader import load_volume_drivers

URI = 'rmv'
NAME = 'action|volume|rmv'
METHODS = ['POST']
