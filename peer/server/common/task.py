from time import sleep
from threading import Thread

def spawn(target, *args, **kwargs):
    th = Thread(target=target, args=args, kwargs=kwargs)
    th.start()
    return th
