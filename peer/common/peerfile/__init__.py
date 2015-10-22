import os
from functools import partial
from peer.common.peerfile.exception import PeerfileNotFound
from peer.common.peerfile.exception import PeerfileUnknownCommand
from peer.common.peerfile.exception import PeerfileMissingCommand

def parse_name(build, argv):
    build['name'] = argv
    return build

def parse_program(build, argv):
    build['program'] = argv
    return build

def parse_cmdline(build, argv):
    build['cmdline'] = argv
    return build

def parse_from(build, argv):
    build['from'] = argv
    return build

def parse_min_core(build, argv):
    build['min_core'] = int(argv)
    return build

def parse_min_mem(build, argv):
    build['min_mem'] = int(argv)
    return build

def parse_cmd(build, argv):
    build['run'].append(['cmd', argv])
    return build

def parse_ps(build, argv):
    build['run'].append(['ps', argv])
    return build

def parse(path):
    pf_path = os.path.join(path, 'Peerfile')
    if not os.path.exists(pf_path):
        raise PeerfileNotFound(pf_path)

    build = {
        'cmdline': '',
        'min_core': 1,
        'min_mem': 512,
        'run': []
    }

    parsers = globals()

    with open(pf_path) as fr:
        n = 0
        for line in fr:
            line = line.strip()
            n += 1

            # comment line
            if line.startswith('#'):
                continue

            # empty line
            if line == '':
                continue

            if ' ' not in line:
                raise PeerfileUnknownCommand('', n)

            _cmd, argv = line.split(' ', 1)
            argv = argv.lstrip()
            cmd = cmd.lower().replace('-', '_')

            fn = 'parse_%s' % cmd
            if fn not in parsers:
                raise PeerfileUnknownCommand(_cmd, n)

            try:
                build = parsers[fn](build, argv)
            except Exception as ex:
                raise PeerfileParseError(_cmd, n, str(ex))

    def _require_command(build, command):
        if build.get(command) is None:
            raise PeerfileMissingCommand(command)

    require_command = partial(_require_command, build)
    map(require_command, ['name', 'program', 'from'])

    return build
