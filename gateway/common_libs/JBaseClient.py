#encoding=utf-8
"""this is not thread-safe"""

import urllib2
import ConfigParser
import logger
import os
import threading
import time
import random
import requests
import urllib
import traceback
import ossattr

class Stat:
    oa = ossattr.OssAttr()

class Error:
    OK = "OK"
    CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND"
    READ_CONF_FAILED = "READ_CONF_FAILED"
    BAD_CONFIG_FORMAT = "BAD_CONFIG_FORMAT"
    NO_META_CONFIG = "NO_META_CONFIG"

    NO_ENDPOINT = "NO_ENDPOINT"
    #BAD_PARAM_ENCODING = "BAD_PARAM_ENCODING",
    #NULL_ENTITY = "NULL_ENTITY",
    #ROUTING_METHOD_NOT_ALLOW = "ROUTING_METHOD_NOT_ALLOW",

    UNKNOWN_ERROR = "UNKNOWN_ERROR"

    CONNECTION_REFUSE = "CONNECTION_REFUSE"
    CONNECT_TIMEOUT = "CONNECT_TIMEOUT"
    READ_TIMEOUT = "READ_TIMEOUT"
    SSL_ERROR = "SSL_ERROR"
    #UNEXPECTED_IO_ERROR = "UNEXPECTED_IO_ERROR",

    LOGICAL_ERROR = "LOGICAL_ERROR"

class Consts:
    RPC_COUNT = "RPC_COUNT"
    RPC_RETA = "RPC_RETA"
    RPC_RETI = "RPC_RETI"
    RPC_QUALITY = "RPC_QUALITY"

class JBaseEnvironment:
    caller_module = ""

    @staticmethod
    def SetCallerName( caller ):
        JBaseEnvironment.caller_module = caller

class JBaseException:
    def __init__(self, err):
        self.err = err

class CaseInsensitiveConfigReader:
    def __init__(self, file_path):
        self.sections = {}
        cfg = ConfigParser.ConfigParser()
        cfg.read( file_path )
        for sect in cfg.sections():
            s = sect.lower()
            self.sections[ s ] = {}
            for opt in cfg.options( sect ):
                self.sections[ s ][opt.lower()] = cfg.get( sect, opt ).strip()

    def get( self, sect, key, default = '' ):
        sect = sect.lower()
        key = key.lower()
        return self.sections.get( sect, {} ).get( key, default )

    def get_int( self, sect, key, default ):
        tmp = self.get( sect, key, '' )
        try:
            tmp = int(tmp)
            return tmp
        except:
            return default

    def sects(self):
        return self.sections.keys()

    def options(self,sect):
        return self.sections.get( sect, {} ).keys()

    def dump(self):
        return json.dumps( self.sections )




class Config:
    def __init__(self, module_name):
        self.module_name = module_name
        self.rel_path = "/client/%s_cli.conf" % module_name
        self.file_path = None
        self.last_check_time = 0
        self.last_load_time = 0

        self.region2option = {}
        self.region2endpoints = {}
        self.region2endpoints_read = {}
        self.region2endpoints_write = {}

    def reload_if_needed( self ):
        if self.file_path is None:
            self.file_path = ConfigLoader.locate_file( self.rel_path )
        if self.file_path is None: raise JBaseException( Error.CONFIG_NOT_FOUND )

        now = time.time()
        if self.last_check_time + 60 < now:
            st = os.stat( self.file_path )
            last_modify_time = st.st_mtime
            if last_modify_time > self.last_load_time:
                self.reload()
                self.last_load_time = now

    def load_region_option( self, cfg, region ):
        region_option = {}
        region_option['connect_timeout'] = cfg.get_int( region, 'connecttimeout', 100 )
        region_option['read_timeout'] = cfg.get_int( region, 'readtimeout', 500 ) 
        self.region2option[region] = region_option

    def reload(self):
        cfg = CaseInsensitiveConfigReader( self.file_path )

        tmp = {}
        regions_pending_get = []
        #get general/regions
        region_count = cfg.get_int( 'general', 'regions', 0 )


        for i in xrange( region_count ):
            option = "region%d" % i
            regions_pending_get.append( cfg.get('general', option, '') )

        if not 'global' in regions_pending_get: regions_pending_get.append( 'global' )

        suffixes = ['','.read','.write']
        for r in regions_pending_get:
            if not r: continue
            r = r.lower()

            self.region2endpoints[ r ] = []
            self.region2endpoints_read[ r ] = []
            self.region2endpoints_write[ r ] = []

            self.load_region_option( cfg, r )
            for s in suffixes:
                endpoint_cnt = cfg.get_int( r, 'endpoints%s' % s, 0 )

                for i in xrange(endpoint_cnt):
                    sect = '%s%s%d' % ( r, s, i )
                    location = cfg.get( sect, 'location', '' )
                    if not location: continue
                    self.region2endpoints[r].append( location )
                    if s == '.read':
                        self.region2endpoints_read[r].append( location )
                    elif s == '.write':
                        self.region2endpoints_write[r].append( location )

    def _select_endpoints_dict_by_rw( self, read_or_write = None ):
        ret = self.region2endpoints
        if read_or_write == 'read':
            ret = self.region2endpoints_read
        elif read_or_write == 'write':
            ret = self.region2endpoints_write
        return ret

    def get_endpoint_count( self, region, read_or_write = None ):
        to_check = self._select_endpoints_dict_by_rw( read_or_write )
        if not to_check.has_key( region ):
            region = 'global'
        if not to_check.has_key(region):
            raise JBaseException( Error.NO_ENDPOINT )
        return len( to_check[region] )

    def get_endpoint( self, region, sect = -1, read_or_write = None ):
        to_select = self._select_endpoints_dict_by_rw( read_or_write )
        ep_cnt = self.get_endpoint_count( region, read_or_write )
        if ep_cnt <= 0:
            raise JBaseException( Error.NO_ENDPOINT )
        if sect < 0:
            sect = random.randint( 0, ep_cnt - 1 ) 
        if not to_select.has_key( region ):
            region = 'global'
        if not to_select.has_key(region):
            raise JBaseException( Error.NO_ENDPOINT )
        return to_select[region][ sect % ep_cnt ]

    def get_option( self, region ):
        if not self.region2option.has_key( region ):
            region = 'global'
        return self.region2option[region]
        

class ConfigLoader:
    @staticmethod
    def init():
        if getattr(ConfigLoader, 'inited', False): return
        ConfigLoader.mutex = threading.Lock()
        ConfigLoader.inited = True
        ConfigLoader.cached = {}
        ConfigLoader.search_paths = [
            os.getenv('HOME') + "/jodo/etc",
            "/home/jodo/etc",
        ]
        ConfigLoader.meta = None

    @staticmethod
    def locate_file( file_path ):
        for p in ConfigLoader.search_paths:
            to_check = p + file_path
            if os.path.exists( to_check ) and os.path.isfile( to_check ):
                return to_check
        return None

    @staticmethod
    def get_region( ): 
        with ConfigLoader.mutex:
            if getattr(ConfigLoader,'region',None) is None:
                meta_path = ConfigLoader.locate_file( "/meta.conf" )
                if meta_path is None: raise JBaseException( Error.NO_META_CONFIG )

                cfg = CaseInsensitiveConfigReader( meta_path )
                ConfigParser.region = cfg.get( 'general', 'region', None )

                if ConfigParser.region is None: raise JBaseException( Error.NO_META_CONFIG )

            return ConfigParser.region

    @staticmethod
    def get_config( module_name ):
        with ConfigLoader.mutex:
            if not ConfigLoader.cached.has_key( module_name ):
                tmp = Config( module_name )
                tmp.reload_if_needed()
                ConfigLoader.cached[ module_name ] = tmp
            else:
                tmp = ConfigLoader.cached[ module_name ]
                tmp.reload_if_needed()
            return tmp

class JBaseClient:
    @staticmethod
    def set_default_logger( logger ):
        JBaseClient.logger = logger

    def __init__( self, module2call, region = None ):
        ConfigLoader.init()
        self.log = getattr( JBaseClient, 'logger', None )
        if not self.log:
            self.log = logger.Logging.getLogger( JBaseClient.__name__ )

        self.module2call = module2call
        self.region = region
        self.reset()

    def reset( self ):
        self.round_robin = 0
        self.headers = {
            'User-Agent': 'JBC Py 201803061631'
        }
        self.params = {}
        self.interface2call = ""
        self.round_robin = int(time.time() * 1000)

        self.status_code = 200
        self.last_error = Error.OK
        self.resp_body = ""
        self.post_body = None

    def Call( self, interface ):
        self.interface2call = interface
        return self


    def AddParam( self, key, value ):
        if not value is str and not value is unicode:
            value = str(value)
        self.params[key] = value
        return self

    def AddHeader( self, key, value ):
        self.headers[key] = value
        return self

    def Core( self, method ):
        try:
            st = time.time()
            if not self.region: self.region = ConfigLoader.get_region()
            client_config = ConfigLoader.get_config( self.module2call )
            endpoint = client_config.get_endpoint( self.region )
            url = endpoint.strip("/") + "/" + self.interface2call.strip("/")
            #do http things
            """
            request(method, url, **kwargs)
            Constructs and sends a :class:`Request <Request>`.
                :param method: method for the new :class:`Request` object.
                :param url: URL for the new :class:`Request` object.
                :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
                :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
                :param json: (optional) json data to send in the body of the :class:`Request`.
                :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
                :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
                :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': ('filename', fileobj)}``) for multipart encoding upload.
                :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
                :param timeout: (optional) How long to wait for the server to send data
                    before giving up, as a float, or a :ref:`(connect timeout, read
                    timeout) <timeouts>` tuple.
                :type timeout: float or tuple
                :param allow_redirects: (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
                :type allow_redirects: bool
                :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
                :param verify: (optional) whether the SSL cert will be verified. A CA_BUNDLE path can also be provided. Defaults to ``True``.
                :param stream: (optional) if ``False``, the response content will be immediately downloaded.
                :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
                :return: :class:`Response <Response>` object
                :rtype: requests.Response
            """
            #self.log.debug('will call %s' % url)
            opt = client_config.get_option( self.region )
            r = requests.request( 
                method, 
                url, 
                headers = self.headers, 
                params = self.params, 
                data = self.post_body, 
                timeout = ( opt['connect_timeout'] / 1000.0, opt['read_timeout'] / 1000.0 )
                )

            self.resp_body = r.text
            self.status_code = r.status_code
            if self.status_code != 200:
                self.last_error = Error.LOGICAL_ERROR
            else:
                self.last_error = Error.OK

        except JBaseException, ex:
            self.last_error = ex.err
        except requests.exceptions.ConnectTimeout, ex:
            self.last_error = Error.CONNECT_TIMEOUT
        except requests.exceptions.ConnectionError, ex:
            self.last_error = Error.CONNECTION_REFUSE
        except requests.exceptions.ReadTimeout, ex:
            self.last_error = Error.READ_TIMEOUT
        except Exception, ex:
            self.log.critical( traceback.format_exc() )
            self.last_error = Error.UNKNOWN_ERROR
        finally:
            et = time.time()

            slash_idx = self.interface2call.find('/')
            if slash_idx < 0:
                slash_idx = len(self.interface2call)

            if slash_idx == 0:
                slash_idx = self.interface2call.find('/', slash_idx+1)

            if slash_idx < 0:
                slash_idx = len(self.interface2call)

            path_first = self.interface2call[:slash_idx]
            if not JBaseEnvironment.caller_module:
                Stat.oa.Inc( "%s.%s:%s" % (Consts.RPC_COUNT, self.module2call, path_first ) )
            else:
                Stat.oa.Inc( "%s.%s:%s:%s" % (Consts.RPC_COUNT, self.module2call, path_first, JBaseEnvironment.caller_module) )

            Stat.oa.Inc( "%s.%s:%s" % (Consts.RPC_RETA, self.module2call, self.last_error) )
            Stat.oa.Inc( "%s.%s:%s:%s" % (Consts.RPC_RETI, self.module2call, path_first, self.last_error ) )

            t = int((et-st)*1000)
            k = 0
            while t > 0:
                k += 1
                t >>= 1

            Stat.oa.Inc( "%s.%s:%s:Q%d" % (Consts.RPC_QUALITY, self.module2call, path_first, k) )

            
        return self.last_error

    def Get( self ):
        return self.Core( 'get' )

    def Post( self, body ):
        self.post_body = body
        return self.Core( 'post' )


    


#TEST
def TestLoadRegion():
    ConfigLoader.init()
    print ConfigLoader.get_region()

def TestConfig():
    import json
    c = Config( "jodo_white_list_service" )
    c.reload_if_needed()
    print json.dumps( c.region2option )
    print json.dumps( c.region2endpoints )
    print json.dumps( c.region2endpoints_read )
    print json.dumps( c.region2endpoints_write )
    print c.get_endpoint_count( 'dev13' )
    print c.get_endpoint( 'dev13' )
    print c.get_endpoint( 'dev13' )
    print c.get_endpoint( 'dev13' )

def TestClient():
    import json
    st = time.time()
    for i in range(1,10000):
        c = JBaseClient( "jodo_white_list_service" )
        body = {'expr':"1+2+\"你好\""}
        ret = c.AddParam('a',1).Call("test").Post( json.dumps( body ) )
    et = time.time()
    print "10000 times takes", et - st, "seconds"
    print ret

def RunTests():
    TestLoadRegion()
    TestConfig()
    TestClient()

if __name__ == "__main__":
    RunTests()





