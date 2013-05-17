'''
Created on 2011-6-2

@author: Tanglh
'''

import os,sys,datetime,threading

#import web.

import rbconf.conff as rbcfg
import rbconf.cfgdb as cfgdb
import rblog.worklog as wlog
import rbruntime.dirfile as dfile
import rbaction.BaseAction
import rbaction.Daemons as rbdm
import rbaction.MapReduceAction,rbaction.WorkController as wrkCtrl
import rbruntime.Linux as linux
import rbupgrade.UpgWork as upgwork
import rbupgrade.UpgradeAction as upgaction
 
#sys.setdefaultencoding('utf8')
curpath= os.getcwd()
basepath=curpath+"/workdatas"
webroot=basepath+"/www"
cfgpath=basepath+"/rbconfig"

if __name__ == '__main__':
    pass

def onClearReadedFilesDaemon():
    wrkCtrl.onClearReadedFilesDaemon()
    return

def onZipTranWorks():
    wrkCtrl.onZipTranWorks()
    return

def onCaptureWorks():
    wrkCtrl.onCaptureWorks()
    return

# after 0.8.5
def chkLogger():
    def buildLogFile(ldir,logFN):
        if(type(logFN)==type(ldir)):
            lf=dfile.joinPath(ldir,logFN)
            fileh=open(lf,'a')
            fileh.close()
            
            return lf
            
        return None
        
    if(wlog.LOGFILE is None):
      ldir=dfile.joinPath(basepath, wlog.LOG_PATH)
      dfile.chkCreateDir(ldir) 
      
      wlog.LOGFILE=buildLogFile(ldir,wlog.LOG_FILENAME)
      for extag in wlog.EXLOGTAGS:
          logfn=buildLogFile(ldir,wlog.defaultEXLogName(extag))
          if(logfn is None):continue
          wlog.initEXLogDef(extag,logfn)
          wlog.getExLogger(extag)
      
      return    
      
def onLogger():
    chkLogger()
    log=wlog.getLogger()
    log.debug("test")
    
    return

def onStart():
    wrkCtrl.onPath(curpath)
   
    rbcfg.RUNMSG["COMM"]="STOP"
    
    rbcfg.WEB["tpls"]=webroot
    rbcfg.WEB["tplsA"]=dfile.joinPath(webroot, "WEB-INF") 
    
    cfgdb.onCfg()  
    
    return
 
def onBackendStart():
    def testUpg():
        import rbconf.cfgvol as cfgvol
        
        upga=upgaction.getUpgSchedule("TEST")
        print upga
        if(upga is not None):
                cfgvol.setUPGState(0)
                upga.exe()
                
        return
        
    def realUpg():
        linux.doPrint( "begin upg work"     )
        upgwork.upgWorkMain()
        linux.doPrint( "upg worked  restart remotebox..."     )
        
        linux.remoteBoxRework() #linux.remoteBoxUpgRework() remoteBoxRework()  linux.doReboot()
        return
    
    #testUpg()
    realUpg()
    
    return

def main():
    linux.doPrint( "start upg main")    
    onLogger()
    onStart()
    onBackendStart()
    return

main()