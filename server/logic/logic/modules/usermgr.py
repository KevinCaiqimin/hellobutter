import json

from logic.defines import *
from logic.objs import *
from logic.core import *

class UserMgr:
    _instance = None

    def __init__(self):
        self.users = {}
        self.r = None

    @staticmethod
    def instance():
        if UserMgr._instance is None:
            UserMgr._instance = UserMgr()
        return UserMgr._instance

    def init(self, r):
        self.r = r

    def loadOrCreateUser(self, uid):
        userKey = Define.getCacheKeyUser(uid)
        userJs = self.r.get(userKey)
        dicUser = None
        user = User()
        if userJs is not None:
            dicUser = json.loads(userJs)
            user.load(dicUser)
        else: #create user
            user = User(
                uid = uid,
                name = "unnamed",
                lastUpdate = utils.getNowTime(),
                createAt = utils.getNowTime(),
            )
        return user
        
    def saveUser(self, user):
        dic = {}
        user.save(dic)
        
        userKey = Define.getCacheKeyUser(user.uid)
        userVal = json.dumps(dic)

        Redis = self.r
        
        Redis.set(userKey, userVal)