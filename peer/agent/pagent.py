import base64
import json
from functools import wraps
import socket
from subprocess import Popen, PIPE
import os

base64_encode = lambda s: base64.encodestring(s).replace("\n", "")
base64_decode = lambda s: base64.decodestring(s)

class Response(object):

    @classmethod
    def new(cls, *args, **kwargs): raise NotImplementedError
    def dumps(self): raise NotImplementedError

class StringResponse(Response):
    @classmethod
    def new(cls, text):
        self = cls()
        self.text = text
        return self

    def dumps(self):
        return "#base64:str," + base64_encode(self.text)

class Agent(object):
    def __init__(self):
        self._functions = {}

    def parse_opts(self, optStr):
        class Option(object):
            def __init__(self, func, args):
                self.function = func.replace("-", "_")
                self.arguments = args

        if "," in optStr:
            function, arguments = optStr.split(",", 1)
            if arguments.startswith("#") and "," in arguments:
                fmt, enc = arguments.split(",", 1)
                fmt = fmt[1:]
                fmt, typ = fmt.split(":", 1) if (":" in fmt) else (fmt, "str")
                dec_func = {"base64": base64.decodestring}.get(fmt)
                typ_func = {"str": str,
                            "unicode": unicode,
                            "int": int,
                            "float": float,
                            "json": json.loads}.get(typ)
                if not dec_func:
                    raise Exception("unsupport encoding format: %s" % fmt)
                if not typ_func:
                    raise Exception("unsupport type: %s" % typ)
                arguments = typ_func(dec_func(enc))
        else:
            function, arguments = optStr, ""

        return Option(function, arguments)

    def register(self, response_class=None):
        if response_class is None:
            response_class = StringResponse
        def wrapper(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                resp = f(*args, **kwargs)
                if not isinstance(resp, Response):
                    resp = response_class.new(resp)
                return resp.dumps()
            self._functions[f.__name__] = wrapped
            return wrapped
        return wrapper

    def _call(self, opts):
        if opts.function not in self._functions:
            raise Exception("unsupport function: %s" % opts.function)
        return self._functions[opts.function](opts.arguments)

    def call(self, optStr):

        opts = self.parse_opts(optStr)
        try:
            return self._call(opts)
        except Exception as ex:
            return "#base64:json," + base64_encode(json.dumps({"_error": str(ex)}))

    def simple_call(self, function, arguments=None):
        optStr = function
        if arguments:
            optStr += ',#base64:json,' + base64_encode(json.dumps(arguments))
        return base64_decode(self.call(optStr).split(',', 1)[1])

agent = Agent()

@agent.register()
def get_local_address(arguments=None):
    return socket.gethostbyname(socket.gethostname())

main = agent.call

if __name__ == '__main__':
    print main(__import__('sys').argv[1])
