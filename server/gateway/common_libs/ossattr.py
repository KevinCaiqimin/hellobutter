import socket
class OssAttr:
    def __init__( self ):
        self._udp_cli = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

    def Inc( self, key, value = 1 ):
        try:
            self._udp_cli.sendto( "%s %d" % ( key, value ), ("127.0.0.1",6666) )
        except:
            pass
