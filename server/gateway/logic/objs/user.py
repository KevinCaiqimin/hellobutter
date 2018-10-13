from logic.core import BaseObj

class User (BaseObj):
    def __construct__(self):
        self.channelId = ""
        self.channelUid = ""
        self.uid = 0
        self.token = ""
        self.lastUpdateAt = 0
        self.createAt = 0
        self.loginTime = 0

    def save(self, dic):
        dic["channelId"] = self.channelId
        dic["channelUid"] = self.channelUid
        dic["uid"] = self.uid
        dic["token"] = self.token
        dic["lastUpdateAt"] = self.lastUpdateAt
        dic["createAt"] = self.createAt
        dic["loginTime"] = self.loginTime

    def load(self, dic):
        if dic is None:
            return
        self.channelId = dic.get("channelId")
        self.channelUid = dic.get("channelUid")
        self.uid = dic.get("uid")
        self.token = dic.get("token")
        self.lastUpdateAt = dic.get("lastUpdateAt")
        self.createAt = dic.get("createAt")
        self.loginTime = dic.get("loginTime")