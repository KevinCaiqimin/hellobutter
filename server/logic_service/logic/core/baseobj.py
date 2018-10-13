'realtime battle server heartbeat data'
import json

class BaseObj:
    def __construct__(self):
        pass

    def __init__(self, **kwargs):
        self.__construct__()
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def toJson(self):
        return {}
    
    def toJsonVal(self):
        js = self.toJson()
        return json.dumps(js)