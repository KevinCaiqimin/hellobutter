import json
import JBaseClient
import ossattr
class SyncContext:
    def __init__(self, svr_impl):
        self.syncs = []
        self.svr_impl = svr_impl
        self.ossattr = ossattr.OssAttr()

    def do_sync( self, module_name, dst_idcs ):
        self.svr_impl.log.info('will sync `%s` to idc `%s` for `%s`',
            json.dumps( self.syncs ), dst_idcs, module_name  )
        if len(self.syncs) < 1: return
        for dst_idc in dst_idcs:
            qproxy = JBaseClient.JBaseClient("universal_queueproxy")
            qproxy_payload = {
                'module':module_name,
                'interface':'recv_cross_idc_stream',
                'payload': json.dumps({ 'records': self.syncs }),
                'idc': dst_idc
            }
            qproxy_ret = qproxy.Call("sched").Post( json.dumps( qproxy_payload ) )
            if qproxy_ret != JBaseClient.Error.OK:
                self.svr_impl.log.warn('communicate to queueproxy failed with ret `%s`, will report and ignore!', qproxy_ret)
                self.ossattr.Inc( "ERR:PUSH2QUEUEPROXY:%s" % module_name )
                continue
            resp = qproxy.resp_body
            if resp and json.loads(resp)['code'] != 0:
                self.svr_impl.log.warn('queueproxy return non zero failed `%s`, will report and ignore!', resp)
                self.ossattr.Inc( "ERR:PUSH2QUEUEPROXY:%s" % module_name )
                continue
            self.svr_impl.log.info('push `%s` to queue for idc `%s` done',
                json.dumps( self.syncs ), dst_idc )
            
        self.syncs = None
        self.svr_impl = None

    def append( self, r ):
        self.syncs.append( {
            'name': r.__class__.__tablename__,
            'payload': r.dump( ),
            } ) 


class IdcSyncHelper:
    def __init__(self):
        self.dst_idcs = []

    def set_dst_idcs( self, dst_idcs ):
        self.dst_idcs = dst_idcs

    def sync( self, module ):
        def core( func ):
            def wrap( impl, *args, **kwargs ):
                impl.idc_sync_context = SyncContext( impl )
                ret = func( impl, *args, **kwargs )
                if ret['code'] == 0:
                    impl.idc_sync_context.do_sync( module, self.dst_idcs )
                    impl.idc_sync_context = None
                return ret
            return wrap
        return core
idc_sync_helper = IdcSyncHelper()


