def get_local_address(options):
    import socket
    return socket.gethostbyname(socket.gethostname())

def terminal(options):
    import os
    return os.popen(options).read()

def get_rdp_info(options):
    import os
    dat = os.popen('powershell.exe Get-WmiObject -namespace root/cimv2/terminalservices -class "Win32_TSGeneralSetting"').read()
    lines = []
    cache_line = ''
    for line in dat.split('\n'):
        if line.startswith(' ' * 10):
            cache_line += line.strip()
        else:
            lines.append(cache_line)
            cache_line = line

    o = {}
    for line in lines:
        if line == '':
            if o and 'RDP' in o.get('__RELPATH', ''):
                return '%s, %s' % (o['__SERVER'], o['SSLCertificateSHA1Hash'])
            o = {}
        else:
            try:
                k, v = line.split(':', 1)
                o[k.strip()] = v.strip()
            except:
                pass

    return ','

def main(options):
    import base64
    import json
    try:
        glos = globals()
        if "," in options:
            action, options = options.split(",", 1)
            if options.startswith("#") and "," in options:
                fmt, enc = options.split(",", 1)
                fmt = fmt[1:]
                fmt, typ = fmt.split(':', 1) if (':' in fmt) else (fmt, 'str')
                dec_func = {'base64': base64.decodestring}.get(fmt)
                typ_func = {'str': str,
                            'unicode': unicode,
                            'json': json.loads}.get(typ)
                if not dec_func:
                    raise Exception("unsupport encoding format: %s" % fmt)
                if not typ_func:
                    raise Exception("unsupport tpye: %s" % typ)
                options = typ_func(dec_func(enc))
        else:
            action, options = options, ""
        fn = action.replace("-", "_")
        if fn in glos:
            return glos[fn](options)
        else:
            return "action: %s not found" % action
    except Exception as ex:
        return "unexpect exception: %s" % str(ex)
