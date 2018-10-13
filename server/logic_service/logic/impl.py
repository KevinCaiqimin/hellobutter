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

from modules import *

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
        self.cmdContainer = {}

        UserMgr.instance().init(self.r)

    @staticmethod
    def master_init( ):
        '''init things here( such as some run-time created class'''
        pass

    def child_init( self ):
        pass

    def before_first_request_run( self, svr_config ):
        pass

    @common_libs.jpkit.expose
    @common_libs.jpkit.need_write
    @common_libs.jpkit.use_body
    def serve(self, paramT):
        jsonData = json.loads(paramT)
        loginTime = jsonData.get("loginTime", None)
        token = jsonData.get("token", None)
        uid = jsonData.get("uid", None)
        cmd = jsonData.get("cmd")
        data = jsonData.get("data")
        #TODO validate parameters

        #TODO validate token
        if uid is None:
            return json.dumps({
                "code" : -1,
                "msg" : "invalid params",
            })
        #load data
        user = UserMgr.instance().loadOrCreateUser(uid)

        #process
        ret = user.onserve(cmd, data)
        #synchronize data
        ret["sync"] = {}
        user.sync(ret["sync"])
        #save data
        UserMgr.instance().saveUser(user)

        assert(ret)
        ret["cmd"] = cmd
        ret["serverTime"] = utils.getNowTime()

        return json.dumps(ret)
