import json

def expose( func ):
    func.exposed = True
    return func

def need_write( func ):
    func.need_write = True
    return func

def to_string( tmp ):
    tp = type(tmp)
    if tp is unicode or tp is str:
        return tmp
    return json.dumps( tmp, ensure_ascii=False )

def is_good_interface_name( ifname ):
    return all( i.isdigit() or i in '_.-' or i.isalpha() for i in ifname )

class NotationClass:
    def __init__( self, nt ):
        self.nt = nt

def notation( notation_type ):
    def core( func ):
        func.notation = NotationClass( notation_type )
        return func
    return core

use_body = notation( 'use_body' )
json_body = notation( 'json_body' )
