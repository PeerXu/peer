import os
import gzip
import tempfile

from peer.server.common import config
from peer.server.main import get_app


class Graph(object):
    BUFSIZ = 16 * 1024  # 16k bytes buffer size

    def __init__(self, root):
        self._root = root
        self._config = config.load()
        self._apps = None

        self._init()

    def _init(self):
        if not os.path.exists(self._root):
            os.makedirs(self._root, 0700)

        self._restore()

    def _restore(self):
        _, self._apps, _ = os.walk(self._root).next()

    def _create_application(self, app):
        pass

    def create_application(self, app):
        cli = get_app().get_client()

        res = cli.post('/v1/applications', body=app)
        return res.status == 200

    def delete_application(self, app_id):
        pass

    def register_application(self, app_data, app_checksum, app_compressed_layer):
        self.create_application(app_data)

        app_id = app_data['_id']

        app_root = os.path.join(self._root, app_id)
        os.makedirs(os.path.join(app_root, 0700))

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
