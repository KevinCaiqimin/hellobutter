from logic.core import BaseObj

from logic.objs.bag import Bag
from logic.objs.bag_item import BagItem

from logic.modules.feed import *
from logic.modules.login import *

modules = {
    "feedMgr" : FeedMgr,
    "loginMgr" : FeedMgr,
}

class User(BaseObj):
    def __construct__(self):
        self.uid = 0
        self.name = ""
        self.lastUpdate = 0
        self.createAt = 0
        self.bag = Bag()

        #init requst processors
        self.reqProcessors = {}

        #init modules
        for moduleName in modules:
            inst = modules[moduleName](self)
            setattr(self, moduleName, inst)

    def save(self, dic):
        dic["uid"] = self.uid
        dic["name"] = self.name
        dic["lastUpdate"] = self.lastUpdate
        dic["createAt"] = self.createAt
        dic["bag"] = {}
        self.bag.save(dic["bag"])
        #save modules
        for moduleName in modules:
            saveData = {}
            mod = getattr(self, moduleName)
            saveIntf = getattr(mod, "onsave", None)
            if saveIntf is None:
                print(format("there is no save func can be found, saving will be ignored from %s" % moduleName))
                continue
            saveIntf(saveData)
            dic[moduleName] = saveData

    def load(self, dic):
        if dic is None:
            return
        self.uid = dic.get("uid")
        self.name = dic.get("name")
        self.lastUpdate = dic.get("lastUpdate")
        self.createAt = dic.get("createAt")
        self.bag = Bag()
        self.bag.load(dic.get("bag"))
        #save modules
        for moduleName in modules:
            loadData = dic.get(moduleName, None)
            mod = getattr(self, moduleName)
            loadIntf = getattr(mod, "onload", None)
            if loadIntf is None:
                print(format("there is no load func can be found, loading will be ignored from %s" % moduleName))
                continue
            loadIntf(loadData)

    def sync(self, syncData):
        if syncData is None:
            return
        #save modules
        for moduleName in modules:
            mod = getattr(self, moduleName)
            syncIntf = getattr(mod, "onsync", None)
            if syncIntf is None:
                print(format("there is no sync func can be found, sync will be ignored from %s" % moduleName))
                continue
            data = {}
            syncIntf(data)
            syncData[moduleName] = data

    def login(self):
        #save modules
        for moduleName in modules:
            mod = getattr(self, moduleName)
            intf = getattr(mod, "onlogin", None)
            if intf is None:
                print(format("there is no onlogin func can be found, onlogin will be ignored from %s" % moduleName))
                continue
            intf()

    def ontimer(self, timerName):
        timerIntfName = format("ontimer_%s" % timerName)
        #save modules
        for moduleName in modules:
            mod = getattr(self, moduleName)
            intf = getattr(mod, timerIntfName, None)
            if intf is None:
                print(format("there is no %s func can be found, onlogin will be ignored from %s" % 
                        (timerIntfName, moduleName)))
                continue
            intf()

    def onserve(self, cmd, data):
        intfName = format("onserve_%s" % cmd)
        ret = None
        for moduleName in modules:
            mod = getattr(self, moduleName)
            intf = getattr(mod, intfName, None)
            if intf is None:
                continue
            ret = intf(data)
            return ret

        return {
            "code" : -1,
            "msg" : "no intf found",
        }

    def addItem(self, itemId, itemNum):
        assert(itemNum >= 0)
        bagItem = self.bag.items.get(itemId)
        if bagItem is None:
            bagItem = BagItem(id = itemId, itemNum = 0)
            self.bag.items[itemId] = bagItem
        bagItem.num += itemNum

    def subItem(self, itemId, itemNum):
        assert(itemNum >= 0)
        bagItem = self.bag.items.get(itemId)
        if bagItem is None:
            return
        bagItem.num -= itemNum
        if bagItem.num < 0:
            bagItem.num = 0

    def isItemEnough(self, itemId, itemNum):
        assert(itemNum >= 0)
        bagItem = self.bag.items.get(itemId)
        if bagItem is None:
            return False
        return bagItem.num >= itemNum