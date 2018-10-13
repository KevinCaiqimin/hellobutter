from logic.modules.basemod import BaseMod

class FeedMgr(BaseMod):
    def __init__(self, user):
        self.user = user
        pass

    #specify what data will be saved to dic
    def onsave(self, dic):
        pass

    #load data from specified dic
    def onload(self, dic):
        pass

    #trigger when user login
    def onlogin(self):
        pass

    def ontimer_1s(self):
        pass

    def ontimer_1m(self):
        pass

    def ontimer_1h(self):
        pass

    def ontimer_1d(self):
        pass

    #trigger after a request is processed and need to synchronize user data
    def onsync(self, sync):
        pass

    def onserve_feed(self, data):
        pass