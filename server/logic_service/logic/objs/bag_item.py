from logic.core import BaseObj

class BagItem (BaseObj):
    def __construct__(self):
        self.uid = ""
        self.id = ""
        self.num = 0

    def save(self, dic):
        dic["uid"] = self.uid
        dic["id"] = self.id
        dic["num"] = self.num

    def load(self, dic):
        if dic is None:
            return
        self.uid = dic.get("uid")
        self.id = dic.get("id")
        self.num = dic.get("num")