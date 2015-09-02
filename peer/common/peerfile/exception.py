from peer.common.exception import PeerBaseError

class PeerfileError(PeerBaseError): pass

class PeerfileNotFound(PeerfileError):
    def __init__(self, path):
        self._path = path

    def __str__(self):
        return 'Cannot locate Peerfile: %s' % self._path

    __repr__ = __str__

class PeerfileMissingCommand(PeerfileError):
    def __init__(self, cmd):
        self._cmd = cmd

    def __str__(self):
        return 'Require command %s' % self._cmd

    __repr__ = __str__

class PeerfileUnknownCommand(PeerfileError):
    def __init__(self, cmd, line):
        self._cmd = cmd
        self._line = line

    def __str__(self):
        return '%s: unknown command %s' % (self._line, self._cmd)

    __repr__ = __str__

class PeerfileParseError(PeerfileError):
    def __init__(self, cmd, line, msg):
        self._cmd = cmd
        self._line = line
        self._msg = msg

    def __str__(self):
        return '%s: %s when parsing %s' % (self._line, self._msg, self._cmd)

    __repr__ = __str__
