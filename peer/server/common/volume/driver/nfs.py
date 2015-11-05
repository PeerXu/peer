from peer.server.common.volume.driver._interface import VolumeDriverInterface

from peer.server.config import get_config
import os

CONFIG = get_config()

class NFSVolumeDriver(VolumeDriverInterface):
    NAME = 'NFSVolumeDriver'
    PROTOCOL = 'nfs'

    def _reload(self):
        os.system('exportfs -rv')

    def create(self, volume):
        volume_path = os.path.join(CONFIG['VOLUME_HOME'], volume['name'])

        if os.path.exists(volume_path):
            os.rmdir(volume_path)

        os.mkdir(volume_path)
        with open('/etc/exports', 'a') as fw:
            fw.write('%s\t*(rw,sync,no_root_squash)\n' % volume_path)

        self._reload()

        return CONFIG['VOLUME_NFS_HOST'] + volume_path

    def delete(self, volume):
        volume_path = os.path.join(CONFIG['VOLUME_HOME'], volume['name'])

        if os.path.exists(volume_path):
            os.rmdir(volume_path)

        with open('/etc/exports') as fr:
            lines = fr.readlines()

        new_lines = []
        for line in lines:
            if not line:
                continue
            st = line.split('\t')
            if st[0] != volume_path:
                new_lines.append(line)

        with open('/etc/exports', 'w') as fw:
            fw.write('\n'.join(new_lines))

        self._reload()

    def mount(self, agent, volumes):
        from base64 import encodestring
        script = ''
        for v in volumes:
            uri = v['uri']
            path = uri.split(':')[1].replace('/', '\\')
            drive = v['drive']
            script += 'c:\\windows\\system32\\mount.exe %s %s:\n' % (path, drive)

        encscript = encodestring(script).replace('\n', '')
        script = 'c:\\python27\\python.exe -c "print __import__(\'base64\').decodestring(\'%s\')" > c:\\users\\public\\peeragent\\mount.bat' % encscript
        agent.run_cmd(script)

DRIVER = NFSVolumeDriver
