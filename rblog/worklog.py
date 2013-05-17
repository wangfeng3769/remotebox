'''
Created on 2011-6-2

@author: Tanglh
'''

import logging,logging.handlers,sys,traceback
#import rbruntime.dirfile as dfile

_logger_=None
LOG_PATH='/rblog/'
FULL_PATH=''
LOG_FILENAME = 'log.txt'
LOGFILE=None
BLOGMSG="_status"

'''
_ex_loggers_={'DB':{'File':None,'Log':None}}
'''
EXLOGTAGS=["DB"]
_ex_loggers_={}

def getLogger():
   global   _logger_
   logfile=LOGFILE
   if(_logger_ is None):
       _logger_=logging.getLogger("sys_status")
       print "_logger_",_logger_
       _logger_.setLevel(logging.DEBUG)
       '''
       logfile=LOG_FILENAME
       if(basepath is not None and type('')==type(basepath)):
           logfile=dfile.joinPath(basepath, logfile)
           dfile.chkCreateDir(logfile)
       '''    
       handler=logging.handlers.RotatingFileHandler(logfile,maxBytes=(1024*1024*3),backupCount=99)
       formatter=logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
       handler.setFormatter(formatter)
       _logger_.addHandler(handler)
   return _logger_
def getExLogger(extag):
    if(extag not in _ex_loggers_):
        return getLogger()
    
    logdef=_ex_loggers_[extag]
    if(type(logdef)<> type({}) or "File" not in logdef):
        return getLogger()
    
    if("Log" not in logdef): logdef["Log"]=None
    if( logdef["Log"] is None):
        logdef["Log"]=buildLogger(logdef["File"],extag+"_"+BLOGMSG)
    
    return logdef["Log"]

def defaultEXLogName(extag):
    if(extag in EXLOGTAGS):
        return extag+LOG_FILENAME
    
    return None
    

def initEXLogDef(extag,filename=None):
    if(extag not in EXLOGTAGS or type(filename)<>type(LOG_FILENAME)):
        return 
     
    _ex_loggers_[extag]={'File':filename,'Log':None}
    
    return

def buildLogger(logfile,logmsg=BLOGMSG):
    rlogger=logging.getLogger(logmsg)
    print "rlogger",rlogger
    rlogger.setLevel(logging.DEBUG)
    
    handler=logging.handlers.RotatingFileHandler(logfile,maxBytes=(1024*1024*3),backupCount=99)
    formatter=logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    rlogger.addHandler(handler)
       
    return rlogger
def getLogFile():
    logfile=LOGFILE
    if(logfile is None):
        logfile=sys.stdout
        
    return logfile

def doTraceBack():
    #traceback.print_exc(file=getLogFile())
    getLogger().error(traceback.format_exc())
    return 
    
def doExTraceBack(extag):
    getExLogger(extag).error(traceback.format_exc())
    return