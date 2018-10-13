import socket
import fcntl
import struct
import ConfigParser
import json
import os

def get_ip_address( ifname ):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = (s.getsockname()[0])
    s.close()
    return ip

class ServerConfig:
    def __init__(self):
        self.sections = {}

    def set( self, sect, key, value ):
        sect = sect.lower()
        key = key.lower()
        if not self.sections.has_key( sect ):
            self.sections[sect] = {}
        self.sections[sect][key] = value

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

class ServerConfigLoader:
    @staticmethod
    def deal_config( svr_config, config_path, role = '' ):
        cfg = ConfigParser.ConfigParser()
        cfg.read( config_path )
        if role:
            for sect in cfg.sections():
                if sect.find(".") > 0:
                    sect_role = sect.split(".")[0]
                    if sect_role.lower() != role.lower() and sect_role != 'default': continue
                    real_sect = sect.split(".")[1]
                else:
                    real_sect = sect

                real_sect = real_sect.lower()

                for opt in cfg.options( sect ):
                    svr_config.set( real_sect, opt, cfg.get( sect, opt ) )
        else:
            for sect in cfg.sections():
                for opt in cfg.options( sect ):
                    svr_config.set( sect, opt, cfg.get( sect, opt ) )
            

        for sect in svr_config.sects():
            for opt in svr_config.options( sect ):
                v = svr_config.get( sect, opt )

                if v.find("${") >= 0:
                    if v.find("${innerip}") >= 0:
                        v = v.replace( "${innerip}", get_ip_address( 'eth0' ) )
                    if v.find("${module}") >= 0:
                        v = v.replace( "${module}", svr_config.get( 'general', 'module' ) )
                        
                    svr_config.set( sect, opt, v )



    @staticmethod
    def load( primary_config, secondary_config = '' ):
        svr_config = ServerConfig()
        ServerConfigLoader.deal_config( svr_config, primary_config )
        if secondary_config:
            ServerConfigLoader.deal_config( svr_config, secondary_config )
        return svr_config

    @staticmethod
    def locate_path_root( ):
        paths = ["/home/etc/", os.path.expanduser("~/etc/"), os.path.expanduser("~/etc/")]
        for p in paths:
            if os.path.exists( p ): return p
        return ""

    @staticmethod
    def load_by_name( service_name ):
        root = ServerConfigLoader.locate_path_root( )
        if not root:
            raise Exception( 'config file root path does not exist!' )

        meta_path = root + service_name + "_meta.conf"
        tmp_cfg = ServerConfig()
        ServerConfigLoader.deal_config( tmp_cfg, meta_path )
        role = tmp_cfg.get( 'general', service_name + ".role" )
        if not role:
            role = tmp_cfg.get( 'general', 'role' )

        if not role:
            meta_path = root + "meta.conf"
            tmp_cfg = ServerConfig()
            ServerConfigLoader.deal_config( tmp_cfg, meta_path )
            role = tmp_cfg.get( 'general', service_name + ".role" )
            if not role:
                role = tmp_cfg.get( 'general', 'role' )

        svr_config = ServerConfig( )
        svr_cfg_path = root + "server/" + service_name + "_svr.conf"
        if not os.path.exists( svr_cfg_path ):
            raise Exception( 'config file `%s` not found' % svr_cfg_path )
        ServerConfigLoader.deal_config( svr_config, svr_cfg_path, role )
        return svr_config

