import os
import zlib
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

        res = cli.post('/v1/applications', data=app)
        return res.status == 201

    def delete_application(self, app_id):
        pass

    def register_application(self, app_data, app_checksum, app_compressed_layer_response):
        self.create_application(app_data)

        app_id = app_data['_id']

        app_root = os.path.join(self._root, app_id)
        if not os.path.exists(app_root):
            os.makedirs(app_root, 0700)

        # TODO(Peer): match checksum before decompress
        tmp_img = tempfile.NamedTemporaryFile(delete=False)
        try:
            decompress_obj = zlib.decompressobj(16 + zlib.MAX_WBITS)
            buf = app_compressed_layer_response.read(self.BUFSIZ)
            while len(buf):
                tmp_img.write(decompress_obj.decompress(buf))
                buf = app_compressed_layer_response.read(self.BUFSIZ)
            os.rename(tmp_img.name, os.path.join(app_root, 'img'))
        finally:
            if os.path.exists(tmp_img.name):
                os.unlink(tmp_img.name)
