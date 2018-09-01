import gunicorn.glogging
import logging, os
import threading
import datetime, time

class MFileHandler( logging.FileHandler ):
    console = False

    def __init__(self, logpath, console = False ):
        self.logpath = logpath
        if not self.logpath.endswith( "/" ):
            self.logpath += "/"
        self.last_check_time = 0
        self.fp = None
        self.last_filename = ""
        self.new_filename = ""
        self.console = console
        self.lock = threading.Lock()
        self.prepare_fp()
        super( MFileHandler, self ).__init__( self.last_filename )

    def prepare_fp( self ):
        with self.lock:
            now = time.time()
            if self.fp == None or int(now / 60) - int(self.last_check_time /60) >= 1:
                dt = datetime.datetime.fromtimestamp(now)
                self.new_filename = "%s%04d%02d%02d%02d.log" % ( self.logpath, dt.year, dt.month, dt.day, dt.hour )
                self.last_check_time = now

            if self.fp == None or self.new_filename != self.last_filename:
                if self.fp: self.fp.close()
                self.fp = open( self.new_filename, "a+" )
                self.last_filename = self.new_filename

    def emit( self, record ):
        tmp = self.format( record )
        self.prepare_fp()
        if self.console:
            print(tmp + "\n")
        self.fp.write( tmp + "\n" )
        try:
            self.fp.flush()
        except:
            #there's nothing i can do here
            pass

class Logging:

    @staticmethod
    def getLogger(name = __name__, log_level = "debug", log_file = None, console = False):
        ## get log level.
        log_level = Logging.getLogLevel(log_level)

        ## create logger
        logger = logging.getLogger(name)
        logger.propagate = False

        ## create log handler.
        if len(logger.handlers) <= 0:
            if log_file is not None:
                handler = MFileHandler( log_file, console )
            else:
                handler = logging.StreamHandler()

            formatter = logging.Formatter("%(asctime)s.%(msecs)03d\t%(name)s\t%(process)d\t%(levelname)s\t%(filename)s:%(funcName)s:%(lineno)d\t%(message)s", "%Y-%m-%d@%H:%M:%S")
            handler.setFormatter(formatter)

            logger.addHandler(handler)
            logger.setLevel(log_level)

        return logger


    @staticmethod
    def getLogLevel(log_level):
        log_level = getattr(logging, log_level.upper(), None)
        if log_level is None: raise Exception("No such log level.")
        return log_level


def GetLoggerClass( appname, logpath, loglevel ):
    class CustomLogger( gunicorn.glogging.Logger ):
        def __init__(self, cfg):
            super( CustomLogger, self ).__init__( cfg )
            self.access_log = Logging.getLogger( appname, loglevel, logpath )
            self.access_log.setLevel( logging.INFO )
            self.error_log = Logging.getLogger( appname, loglevel, logpath )

    return CustomLogger
