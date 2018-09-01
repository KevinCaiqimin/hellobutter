import random
import threading
import time

from baseobj import BaseObj
from xthread import XThread

class XTimer(BaseObj):
    firstDelay = 0
    intvl = 0
    callback = None
    repeatTimes = -1

    _running = False
    _timer = None
    _repeatedTimes = 0

    _lastDoTime = 0
    def run(self):
        while self._running:
            nowTime = time.time()
            if nowTime > self._lastDoTime + self.intvl:
                if self.callback is not None:
                    self.callback()
                self._repeatedTimes += 1
                self._lastDoTime = nowTime
            if self.repeatTimes > 0 and self._repeatedTimes >= self.repeatTimes:
                self._running = False
            time.sleep(0.001)

    def start(self):
        self._running = True
        _timer = XThread(target=self.run, args=())
        _timer.start()

    def stop(self):
        if not self._running:
            return
        self._running = False
        if self._timer == None:
            return
        self._timer.cancel()