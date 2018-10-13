import sys
if __name__ == "__main__":
    sys.path.append('..')

import common_libs
import redis
import random
import json
import time
import math
import traceback
import math
import traceback
import signal

from redisext import RedisExt

from core import *
from defines import *
from objs import *

class ServerLogicImpl:
    
    def __init__(self, svr_config):
        self.svr_config=svr_config
        self.module = svr_config.get('general', 'module', 'notset')
        self.log = common_libs.Logging.getLogger( 
            self.module,
            svr_config.get( 'general', 'loglevel', 'info' ),
            svr_config.get( 'general', 'logpath', '/home/logs' ),
            True
		)
        #region innitialization
        redis_ip = self.svr_config.get('redis', 'ip')
        redis_port = int(self.svr_config.get('redis', 'port'))
        redis_password = self.svr_config.get('redis', 'password', '')
        #pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        pool = redis.ConnectionPool(host=redis_ip, port=redis_port, db=0, password=redis_password)
        r = redis.Redis(connection_pool=pool)
        self.r = r
        self.log.info('redis initialized ')
        #register container for every module

    @staticmethod
    def master_init( ):
        '''init things here( such as some run-time created class'''
        pass

    def child_init( self ):
        pass

    def before_first_request_run( self, svr_config ):
        pass

    def loadOrCreateUser(self, channelId, channelUid):
        userKey = Define.getCacheKeyChannelUser(channelId, channelUid)
        userJs = self.r.get(userKey)
        dicUser = None
        user = User()
        if userJs is not None:
            dicUser = json.loads(userJs)
            user.load(dicUser)
        else: #create user
            user = User(
                channelId = channelId,
                channelUid = channelUid,
                lastUpdateAt = utils.getNowTime(),
                createAt = utils.getNowTime(),
            )
        return user
        
    def saveUser(self, user):
        dic = {}
        user.save(dic)
        
        userKey = Define.getCacheKeyChannelUser(user.uid)
        userVal = json.dumps(dic)

        Redis = self.r
        
        Redis.set(userKey, userVal)

    @common_libs.jpkit.expose
    @common_libs.jpkit.need_write
    @common_libs.jpkit.use_body
    def login(self, paramT):
        jsonData = json.loads(paramT)
        channelId = jsonData.get("channelId", None)
        channelUid = jsonData.get("channelUid", None)
        
        if channelId is None or channelUid is None:
            return json.dumps({
                "code" : -1,
                "msg" : "invalid params",
            })
        Redis = self.r
        #load data
        succ = RedisExt.optimLock(self.r, Define.getLockKeyChannelUser(channelId, channelUid), 10)
        if not succ:
            return json.dumps({
                "code" : -1,
                "msg" : "failed with lock",
            })
        try:
            user = self.loadOrCreateUser(channelId, channelUid)
            if user.uid is None or user.uid == 0:
                longKey = Define.getCacheKeyUid()
                # print(longKey)
                Redis.setnx(longKey, 0)
                uid = Redis.incr(longKey)
                user.uid = uid
            token = utils.randToken(8)
            user.token = token
            user.loginTime = utils.getNowTime()

            self.saveUser(user)

            return json.dumps({
                "channelId" : channelId,
                "channelUid" : channelUid,
                "uid" : uid,
                "token" : token,
                "loginTime" : user.loginTime,
            })
        except:
            exceInfo = traceback.format_exc()
            self.log.error("shit happends here: " + exceInfo)
        finally:
            RedisExt.optimUnlock(self.r, Define.getLockKeyChannelUser(channelId, channelUid))
