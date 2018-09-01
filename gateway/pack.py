import os
import datetime

def GetFileList( parent ):
    for m in os.listdir( parent ):
        if m.startswith("."): continue
        full = parent + "/" + m
        if os.path.isdir( full ):
            for ch in GetFileList( full ):
                yield ch
        else:
            if full.startswith( "build/" ): continue
            yield full

def Work( src_path, dst_tar ):
    files = []
    for f in GetFileList( src_path ):
        if f.endswith('.txt') or f.endswith(".py") or f.endswith(".sh"): files.append( f )

    cmd = "tar -cf %s %s" % ( dst_tar, " ".join(files) )
    ret = os.system(cmd)
    if ret == 0:
        print "packed in %s" % dst_tar


if __name__ == "__main__":
    Work( ".", "build/match_service_%s.tar" % datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
