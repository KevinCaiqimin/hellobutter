from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import common_libs
from logic import ServerLogicImpl
import time
import json
import urllib

import multiprocessing
import gunicorn.app.base
from gunicorn.six import iteritems

import os

import traceback
import math

class Entry( gunicorn.app.base.BaseApplication ):
    def __init__(self, svr_config, gunicorn_config ):
        self.module = svr_config.get('general', 'module', 'notset')
        self.log = common_libs.Logging.getLogger( 
            self.module,
            svr_config.get( 'general', 'loglevel', 'info' ),
            svr_config.get( 'general', 'logpath', self.module + ".log" ),
            True
		)

        self.svr_config = svr_config
        self.log.info("started on %s:%d with %d workers",
            svr_config.get('general', 'ip', '127.0.0.1'),
            svr_config.get_int('general', 'port', 55555),
            svr_config.get_int('general', 'workers', 32) )
        self.read_only = svr_config.get_int('general', 'serverreadonly', 0)

        self.ossattr = common_libs.OssAttr()
        self.gunicorn_config = gunicorn_config

        self.worker = None
        self.first_run = False

        self.env = None

        self.this_interface_found = False

        super(Entry, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.gunicorn_config)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.handle_requests

    def child_init( self ):
        try:
            if not self.worker:
                self.worker = ServerLogicImpl( self.svr_config )
                ci = getattr(self.worker, 'child_init', None)
                if ci: 
                    ci()
        except:
            self.log.critical( 'child init throws exception!' )
            self.ossattr.Inc( 'ERR_CHILD_INIT_FAILED.%s' % self.module )

    def master_init( self ):
        mi = getattr( ServerLogicImpl, 'master_init', None )
        if mi: mi()

    def fake_start_response( self, *args, **kwargs ):
        self.sr( *args, **kwargs )
        self.sr_called = True


    def prepare_ctx( self, environ ):
        self._ctx_client_ip = environ['REMOTE_ADDR']
        forward_for_key = 'HTTP_X_FORWARDED_FOR'
        if environ.has_key(forward_for_key):
            self._ctx_client_ip = environ[forward_for_key]


    def handle_requests( self, environ, start_response ):
        self.env = environ
        self.prepare_ctx( environ )
        self.sr_called = False
        self.sr = start_response
        path = environ.get('PATH_INFO', '')
        qs = environ.get('QUERY_STRING', '')
        args = path.strip("/").split("/")
        interface = ''
        if len(args) >= 1:
            interface = args[0]
            args = args[1:]

        tmp = qs.split("&")
        kwargs = {}
        for x in tmp:
            if not x: continue
            idx = x.find("=")
            if idx > 0:
                kwargs[x[:idx]] = urllib.unquote(x[idx+1:])
            elif idx == -1:
                kwargs[x] = ''

        tmp = str(self.doit( interface, *args, **kwargs ))
        if not self.sr_called:
            start_response('200 OK', [
                ('Content-Type','text/plain; charset=utf-8'),
            ])
        yield tmp

    def dispatch( self, worker, interface, *args, **kwargs ):

        if interface == 'health':
            self.ossattr.Inc("HEALTH_CHECK:%s:%s" % (self.module, interface) )
            self.log.info('HEALTH_CHECK called')
            return 'ok'

        intf = getattr( worker, interface, None )
        if not intf or not getattr( intf, 'exposed', False ):
            return {'code':1, 'msg': 'method `%s` not found' % interface }

        self.this_interface_found = True

        set_raw_context_interface = getattr( worker, 'set_raw_context', None )
        if set_raw_context_interface:
            set_raw_context_interface( self.env, self.fake_start_response )

        #reject write requests if the server is read-only
        if self.read_only and getattr( intf, 'need_write', False ):
            return {'code':2, 'msg': 'method `%s` is not allowed on this server' % interface }

        notat = getattr( intf, 'notation', None )
        if notat:
            if notat.nt == 'use_body':
                body = self.env['wsgi.input'].read()
                self.log.info(format("REQUEST: interface: %s, body: %s" % (interface, body)))
                resp = intf( body )
                self.log.info(format("RESPONSE: interface: %s, resp: %s" % (interface, resp)))
                return resp
            if notat.nt == 'json_body':
                body = self.env['wsgi.input'].read()
                try:
                    jp = json.loads( body )
                except:
                    self.log.error("get invalid post data `%s`", body)
                    return {'code':101, 'msg':'payload `%s` is not a valid json' % body}
                return intf( jp )
           
        body = self.env['wsgi.input'].read() 
        return intf( *args, **kwargs )

    def doit( self, interface, *args, **kwargs ):
        return common_libs.jpkit.to_string( self.process( interface, *args, **kwargs ) )

    def process( self, interface, *args, **kwargs ):
        st = time.time()
        self.this_interface_found = False
        try:

            if not self.first_run:
#                self.worker = ServerLogicImpl( self.svr_config )
                self.worker.before_first_request_run( self.svr_config )
                self.first_run= True

            resp = self.dispatch( self.worker, interface, *args, **kwargs )
            if type(resp) is dict and resp.get('code',0) != 0:
                self.ossattr.Inc("SVR_LOGIC_ERROR:%s:%s" % (self.module, interface))
            
            return resp


        except Exception, ex:
            self.log.critical( "shit happened with args %s, kwargs %s, traceback %s",
                ",".join(args), json.dumps(kwargs), traceback.format_exc() )
            if common_libs.jpkit.is_good_interface_name( interface ):
                self.ossattr.Inc("SVR_ERROR:%s:%s" % (self.module, interface) )
            else:
                self.ossattr.Inc("SVR_ERROR:%s:%s" % (self.module, 'bad_interface') )

            return {'code':-1, 'msg': 'internal error'}
        finally:
            #OSSATTR
            et = time.time()
            time_cost = int((et - st) * 1000)
            if self.this_interface_found: 
                self.ossattr.Inc( "REQ_COUNT:%s:%s" % ( self.module, interface ), 1 )
                self.ossattr.Inc( "COST_MS:%s:%s" % (self.module, interface), time_cost )
                level = int( math.log(time_cost / 50 + 1) / math.log(2) )
                self.ossattr.Inc( "COST_LV:%s:%s:%d" % (self.module, interface, level), 1 )
            else:
                self.ossattr.Inc( "NOT_FOUND:%s" % (self.module) )
            if common_libs.jpkit.is_good_interface_name( interface ):
                self.log.info('`%s` finished request from %s in %d ms', interface, self._ctx_client_ip,time_cost )
            else:
                self.log.info('unknown interface call from %s finished request in %d ms', self._ctx_client_ip, time_cost )

class Bridge:
    def __init__(self):
        pass

    @staticmethod
    def post_fork(server, worker):
        Bridge.entry.child_init()

    @staticmethod
    def when_ready(sserver):
        Bridge.entry.master_init()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        svr_config = common_libs.ServerConfigLoader.load( sys.argv[1], sys.argv[2] )
    elif len(sys.argv) == 2:
        svr_config = common_libs.ServerConfigLoader.load( sys.argv[1] )
    else:
        svr_config = common_libs.ServerConfigLoader.load_by_name( "gateway_service" )

    bridge = Bridge()

    g_config = {
        'bind' : '%s:%d' % (svr_config.get('general', 'ip', '127.0.0.1'), svr_config.get_int('general', 'port', 55555) ),
        'workers' : svr_config.get_int('general', 'workers', 32),
        'worker_class' : 'sync',
        'max_requests': svr_config.get_int('general', 'maxloop', 10000),
        'max_requests_jitter': svr_config.get_int('general', 'maxloop_jitter', 5000), 
        'keepalive': svr_config.get_int('general','keepalive',2),
        'logger_class': common_libs.GetLoggerClass( 
            svr_config.get('general', 'module', 'noset'),
            svr_config.get('general', 'logpath', '/home/logs/'),
            svr_config.get('general', 'loglevel', 'info')
        ),
        'accesslog': '-',
        'post_fork': bridge.post_fork,
        'when_ready': bridge.when_ready,
    }

    with open( svr_config.get('general', 'pidfile', '/tmp/noset.pid'), "w" ) as f:
        f.write( str(os.getpid()) )

    ent = Entry(svr_config, g_config)
    Bridge.entry = ent
    ent.run()