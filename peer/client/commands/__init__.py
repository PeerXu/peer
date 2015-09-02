_COMMANDS = None

def load_commands():
    global _COMMANDS

    if _COMMANDS is None:
        from os import walk
        from peer.client import commands
        from importlib import import_module

        _COMMANDS = {}

        path = commands.__path__[0]
        _, dirs, files = walk(path).next()

        modules = dirs + [f.rsplit('.', 1)[0] for f in files if f.endswith('.py')]
        for module in modules:
            try:
                m = import_module('peer.client.commands.%s' % module)
                name = getattr(m, 'NAME')
                command = getattr(m, 'COMMAND')
                if name and command:
                    _COMMANDS[name] = command
            except Exception as ex:
                pass

        return _COMMANDS
