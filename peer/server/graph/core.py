import os
import gzip
import tempfile

from peer.server.common import config
from peer.common.utils import json


class Graph(object):
    BUFSIZ = 16 * 1024  # 16k bytes buffer size

    def __init__(self, root):
        self._root = root
        self._config = config.load()
        self._applications = None

        self._init()

    def _init(self):
        if not os.path.exists(self._root):
            os.makedirs(self._root, 0700)

        self._restore()

    def _restore(self):
        _, self._applications, _ = os.walk(self._root).next()

    def createApplication(self, application):
        pass

    def deleteApplication(self, application_id):
        pass

    def registrApplication(self, app_json, app_checksum, app_compressed_layer):
        app_id = app_json['id']

        app_root = os.path.join(self._root, app_id)
        os.makedirs(os.path.join(app_root, 0700))

        with open(os.path.join(app_root, 'json'), 'w') as f:
            f.write(json.dumps(app_json))

        # TODO(Peer): match checksum before decompress
        with gzip.open(app_compressed_layer, 'rb') as layer, tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
            while True:
                chunk = layer.read(self.BUFSIZ)
                if chunk:
                    tmp.write(chunk)
                else:
                    break

        os.rename(tmp_path, os.path.join(self._root, app_id, 'img'))
