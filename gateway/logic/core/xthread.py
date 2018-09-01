import threading, time, signal
import sys

class XThread(threading.Thread):
    def __init__(self, group = None, target = None, name = None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs, verbose)
        self.setDaemon(True)