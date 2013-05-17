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
import rbdatabase.DBFactory
import rbdatabase.PojoBuilder
import rbweb as tweb
import rbweb.application as wapp
import rbweb.session
import rbsite.RBSite,rbsite.CfgSite
import rbruntime.Linux as linux
import rbcommit.cdtu
 
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
      '''
      wlog.LOGFILE=dfile.joinPath(ldir,wlog.LOG_FILENAME)
      fileh=open(wlog.LOGFILE,'a')
      
      fileh.close()
      '''
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
    wlog.getLogger().debug(webroot)
    
    cfgdb.onCfg()
    #cfgdb.freshConfByDB()
    
    app=webRun()
    
    session = tweb.session.Session(app, tweb.session.DiskStore('sessions'), initializer={'count': 0})
    
    import rbsite.CmdRender as CmdRender
    refs4tpl={'context': session,"vtypeof":type,"cmdsRender":CmdRender.cmdsRender1}
    
    render = tweb.template.render(rbcfg.WEB["tpls"],globals=refs4tpl)
    renderA = tweb.template.render(rbcfg.WEB["tplsA"],globals=refs4tpl)
    rbcfg.WEB["render"]=render
    rbcfg.WEB["renderA"]=renderA
    
    rbcfg.WEB["app"]=app
    
    rbsite.RBSite.regPageCtx4Tpls()
    
    return

def webRun():
     app = wapp.application(tuple(rbcfg.WEB["urls"]), rbcfg.WEB["refs"])
     app.bindAddr(("0.0.0.0",rbcfg.WEB["port"]))
     # app.runbasic()
     # rbweb.webapi.config.debug=False
     return app
 
def onBackendStart():
    wrkCtrl.onRunningingDaemonPool()
    onClearReadedFilesDaemon()
    onZipTranWorks()
    onCaptureWorks()  
    
    cfgdb.setRunWhenStart() 
    if(rbcfg.RUNMSG["COMM"]=="OK"):
        wrkCtrl.doStart()
        
    return

def runWebber():
    def dorunbasic():
            rbcfg.WEB["app"].runbasic()
            return 
    th=threading.Thread(target=dorunbasic)
    #th.setDaemon(True)
    th.start()

    return

def main():
    linux.doPrint( "start main")    
    onLogger()
    onStart()
    onBackendStart()
    #pool=rbdatabase.PojoBuilder._InnerPool()
    #rbcfg.WEB["app"].runbasic()
    runWebber()
    linux.doPrint( "started main"     )
    return

main()