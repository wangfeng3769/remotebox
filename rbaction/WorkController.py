'''
Created on 2011-8-31

@author: Tanglh
'''

import os,sys,threading,datetime
import BaseAction,MapReduceAction,Daemons,DeamonPool
import rbconf.conff as rbcfg
import rbconf.cfgcmd as cfgcmd
import rbconf.cfgdb as cfgdb
import rbconf.cfgvol as cfgvol
import rbruntime.dirfile as dfile
import rbdatabase.PojoBuilder as pjbuilder
import rbdatabase.Pojos as rbpjs
import rblog.worklog as wlog

tranZipDaemonPools={'RunningPool':None,'StopingPool':None,'StopedPool':None,'MonitorRestart':None}
captureDaemonPools={'RunningPool':None,'StopingPool':None,'StopedPool':None,'MonitorRestart':None}
'''
tranZipRunningDaemonPool=None
tranZipStopingDaemonPool  =None
tranZipStopedDaemonPool=None
tranZipMonitorRestartDaemon=None

captureRunningDaemonPool=None
captureStopingDaemonPool=None
captureStopedDaemonPool=None
captureMonitorRestartDaemon=None
'''

def onPath(curpath):
    if(curpath is None ):curpath= os.getcwd()
    rbcfg.apppath=dfile.joinPath(curpath, rbcfg.apppath)
    rbcfg.basepath=dfile.joinPath(curpath, rbcfg.basepath)
    rbcfg.webroot=dfile.joinPath(rbcfg.basepath,rbcfg.webroot)
    rbcfg.cfgpath=dfile.joinPath(rbcfg.basepath,rbcfg.cfgpath)
    
    #after 0.8.7
    cfgvol.onWorkPath(curpath)
    
    return
    
def onRunningingDaemonPool():
    if(tranZipDaemonPools['RunningPool'] is None):
        tranZipDaemonPools['RunningPool']=DeamonPool.RunningDaemonPool()   
    if(captureDaemonPools['RunningPool'] is None):
        captureDaemonPools['RunningPool']=DeamonPool.RunningDaemonPool()  
    
    return
    
def onTranZipDaemonPool():    
    if(tranZipDaemonPools['StopingPool'] is None):
        tranZipDaemonPools['StopingPool']=DeamonPool.TranZipStopingDaemonPool()
        
    if(tranZipDaemonPools['StopedPool'] is None):
        tranZipDaemonPools['StopedPool']=DeamonPool.TranZipStopedDaemonPool(tranZipDaemonPools['StopingPool'])
        
    if(tranZipDaemonPools['MonitorRestart'] is None):
        tranZipDaemonPools['MonitorRestart']=Daemons.MonitorRestartDaemon(tranZipDaemonPools['StopedPool'])
        
    return

def onCaptrueDaemonPool():
    if(captureDaemonPools['StopingPool'] is None):
        captureDaemonPools['StopingPool']=DeamonPool.CaptureStopingDaemonPool()
        
    import rbdatabase.PojoBuilder as pjb
        
    if(captureDaemonPools['StopedPool'] is None):
        captureDaemonPools['StopedPool']=DeamonPool.CaptureStopedDaemonPool(captureDaemonPools['StopingPool'],pjb.DBPool)
        
    if(captureDaemonPools['MonitorRestart'] is None):
        captureDaemonPools['MonitorRestart']=Daemons.MonitorRestartDaemon(captureDaemonPools['StopedPool'])
        
    return

def onClearReadedFilesDaemon():
    cdm=Daemons.ClearReadedFilesDaemon(rbcfg.basepath)
    
    cdm.start()
    #print "onClearReadedFilesDaemon start %s "  % datetime.datetime.now()
    return

def onZipTranWorks():
    onTranZipDaemonPool()
    rdms=Daemons.ZipTranWorks(rbcfg.basepath,delaySec=5)
    
    tranZipDaemonPools['RunningPool'].extend(rdms)
    tranZipDaemonPools['StopedPool'].extend(rdms)
    
    for rdm in rdms:
        rdm.regPool(tranZipDaemonPools['StopingPool'],tranZipDaemonPools['StopedPool'])# reg DaemonPool
    
   # print "onZipTranWorks start %s "  % datetime.datetime.now()
    return

def onCaptureWorks():
    #rbdatabase.PojoBuilder.DBPool=rbdatabase.PojoBuilder.DBWrapPool()
    onCaptrueDaemonPool()
    mdms=Daemons.CaptureWorks(rbcfg.basepath,delaySec=10) # delay 10 sec to start()
    
    captureDaemonPools['RunningPool'].extend(mdms)
    captureDaemonPools['StopedPool'].extend(mdms)
    
    for mdm in mdms:
      mdm.regPool(captureDaemonPools['StopingPool'],captureDaemonPools['StopedPool'])# reg DaemonPool
    
    #print "onCaptureWorks start %s "  % datetime.datetime.now()
    return

def refreshRunnersDaemonPools(dmon):
    if(dmon is None):return
    dmon.initRunners()
           
    return

def refreshRealPRunnersDaemonPools(*arg):  
    dmon=None
    if(captureDaemonPools['RunningPool'] is not None):
        for rd in captureDaemonPools['RunningPool'].all():
            if(rd._imptype=="REALP")  :
                dmon=rd
                break
        
    refreshRunnersDaemonPools(dmon)
    return
        

def onStop():
    if(rbcfg.RUNMSG["COMM"] is "STOP"):return
    cfgcmd.commCmd("STOP")
    cfgcmd.notifyCommCmd()
    #rbcfg.RUNMSG["COMM"]="STOP"
    
    doStop()
        
    return

def doStop():
    if(tranZipDaemonPools['RunningPool'] is not None):
        for rdm in tranZipDaemonPools['RunningPool'].all():
           rdm.stop()
    
    if(captureDaemonPools['RunningPool'] is not None):
        for mdm in captureDaemonPools['RunningPool'].all():
            mdm.stop()
        
    return

def onStart(): 
    if(rbcfg.RUNMSG["COMM"]=="OK"):return
    #rbcfg.RUNMSG["COMM"]="OK"
    '''
    cfgcmd.commCmd("OK")
    cfgcmd.notifyCommCmd()
    '''
    
    cfgdb.setRunWhenStart(cfgdb.freshIMPLEMENTSByDB,cfgdb.freshIMPLEMENTADDSByDB,refreshRealPRunnersDaemonPools)
    if(rbcfg.RUNMSG["COMM"]=="OK"):
        doStart()
        wlog.getLogger().debug("WorkdoStarted")
    
    return

def doStart():
    if(tranZipDaemonPools['MonitorRestart'] is not None):tranZipDaemonPools['MonitorRestart'].start()
    if(captureDaemonPools['MonitorRestart'] is not None):captureDaemonPools['MonitorRestart'].start()
    
    return