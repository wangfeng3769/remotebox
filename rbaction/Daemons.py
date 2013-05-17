'''
Created on 2011-6-17

@author: Tanglh
'''

import os,sys,threading,datetime,time
import BaseAction,MapReduceAction
import rbconf
import rbconf.conff as rbcfg
import rbconf.cfgcmd as cfgcmd
import rbruntime.dirfile as dfile
import rbruntime.Linux as linux
import rbdatabase.PojoBuilder as pjbuilder
import rbdatabase.Pojos as rbpjs
import rblog.worklog as wlog
import rberror.Errors as errs

capdaemons={}

'''
   a run framewoork for Daemon
'''
class _BaseDaemon:
    def __init__(self,basepath,imptype=None,detaSec=datetime.timedelta(seconds=30),delaySec=0):
        self._basepath=basepath
        self._imptype=imptype
        self._wkpth=basepath
        
        if(not (imptype is None) ):
            if(imptype in rbcfg.IMPLEMENTS):
              refp=rbcfg.IMPLEMENTS[imptype]["PATH"]
              self._wkpth=dfile.joinPath(self._wkpth, refp)
              
        self._can=True
        self._started=False
        self._stoped=False
        self._posted=False
        self._last=None   # datetime.datetime.now()
        self._now=None
        
        self._dtdelta=detaSec
        self._timer=None
        if(type(basepath)==type('')):
           self._timer=threading.Timer(delaySec,self._exe)
        
        return
    
    def _canWork(self):
        return self._can

    def _donotify(self):
        pass
    
    def _run(self):
        self._last=self._now
    
    def _before1(self):
        #self._stoped=False
        '''
        if(rbcfg.RUNMSG["COMM"]=="STOP"):#todo stop
            self._stoped=True
            return False
        '''
        if(self._posted is True):self._posted=False
        ok=self._canWork()  #todo stop
        if(ok==False):
            return ok
        
        self._now=datetime.datetime.now()
        if(self._last is None):
            return ok
        
        ok=(self._dtdelta<self._now-self._last)
        
        return ok
    
    def _before(self):
        if(self._posted is True):self._posted=False
        ok=self._canWork()  #todo stop
        if(ok==False):
            return ok
        
        self._now=datetime.datetime.now()
        if(self._last is None):
            return ok
        
        dd1=self._now-self._last
        slp=self._dtdelta.seconds-dd1.seconds
        if(slp>0):
           linux.doPrint( "Map Sleep:",slp)
           time.sleep(slp)
        
        return ok
    
    def _post(self):
        self._donotify()
        self._posted=True
        return
    
    def _work(self):
        if(self._before()==True):
                self._run()
        
        self._post()
        return
    
    def _exe(self):
        #self._stoped=False
        while True:
            #self._onstoped()
            if(self._stoped==True):
              if(self._posted is False):    self._post()
              self._onstoped()  # my carrier is failed,sorry
              continue
            
            self._work()
            self._onstoped()
        return 
    
    def start(self,stoped=False):
        if(self._timer is None):return
        wlog.getLogger().debug("Daemon tostart"+str(self))
        linux.doPrint( "Daemon tostart"+str(self))
        if self._started is False:
            self._started=True    
            self._timer.start()
            wlog.getLogger().debug("Daemon started"+str(self))
            linux.doPrint( "Daemon started"+str(self))
        
        self._stoped=stoped
        return 
        
    
    def stop(self):
        self._stoped=True
        
        return
    
    def _onstoped(self):
        pass
    
class _BasePooledDaemon(_BaseDaemon):
    def __init__(self,basepath,imptype,detaSec,delaySec=0):     
        _BaseDaemon.__init__(self,basepath,imptype,detaSec,delaySec)
        
        self._stopingPL=None
        self._stopedPL=None
        self.done=True
        #if(imptype in rbcfg.RUNMSG and rbcfg.RUNMSG[imptype] )
        return
    
    def chkStart(self):#self._imptype
        
        if(self._imptype is None and self._imptype not in rbcfg.RUNMSG):
            return True
        #wlog.getLogger().debug(self._imptype+"chkStart"+rbcfg.RUNMSG[self._imptype]["CMD"])
        return rbcfg.RUNMSG[self._imptype]["CMD"] not in cfgcmd.DISENLECMD
    
    def regPool(self,stopingPL,stopedPL):
        self._stopingPL=stopingPL
        self._stopedPL=stopedPL
        
        return
    
    def start(self):
        #self._stoped=False
        #if(not self.chkStart()):self._stoped=True
        _BaseDaemon.start(self,not self.chkStart())
        
        return
        
    def stop(self):
        if(self._stopingPL is not None ):
            impt=""
            if(type(self._imptype)==type('')):impt=self._imptype
            wlog.getLogger().debug(impt+"_stopingPL.append:"+str(self))
            #print impt+"_stopingPL.append:"+str(self)
            self._stopingPL.append(self)
            if(not self.chkStart()):
                self._onstoped()
        self._stoped=True
        return
    
    def _onstoped(self):
        #if(self._imptype is "BASE"):print self._imptype+":_onstoped:"+str(self);wlog.getLogger().debug(self._imptype+":_onstoped:"+str(self))
        if(self._stopingPL is not None  and self._stopedPL is not None and self._stopingPL.included(self)  and not self._stopedPL.included(self) ):
            impt=""
            if(type(self._imptype)==type('')):impt=self._imptype
            print impt+"_stopedPL.append:"+str(self)
            wlog.getLogger().debug(impt+"_stopedPL.append:"+str(self))
            self._stopedPL.append(self)
            #time.sleep(3) 
            #self._stopedPL.restart()
            
        return

def ClearReadedFilesDaemon(basepath,imptype=None,detaSec=datetime.timedelta(seconds=30)):
    return   _ClearReadedFilesDaemon(basepath,imptype,detaSec)  
'''
   clear all data files in basepath
'''    
class _ClearReadedFilesDaemon(_BaseDaemon):   
    def __init__(self,basepath,imptype,detaSec,delaySec=0):     
        _BaseDaemon.__init__(self,basepath,imptype,detaSec,delaySec)
        
        self.runner=BaseAction.ClearReadedFilesAction(self._wkpth)
        return
    
    def _run(self):
        _BaseDaemon._run(self)
        self.runner.exe()
        
        return

def ReduceZipTranDaemon(basepath,imptype,detaSec=None,delaySec=0):
    if(imptype is None or not (imptype in rbcfg.IMPLEMENTS)) :
            raise errs.RbErr("error imptype" +imptype)
        
    if(detaSec is None):
        detaSec=datetime.timedelta(seconds=rbcfg.IMPLEMENTS[imptype]["TIMER"])
        
    return   _ReduceZipTranDaemon(basepath,imptype,detaSec,delaySec)  

'''
 one imptypes to one ReduceAction 
'''    
class _ReduceZipTranDaemon(_BasePooledDaemon):  
    def __init__(self,basepath,imptype,detaSec=datetime.timedelta(seconds=30),delaySec=0):    
        if(imptype is None) :
            raise errs.RbErr("none imptype")
        
        _BasePooledDaemon.__init__(self,basepath,imptype,detaSec,delaySec)
        #refp=rbcfg.IMPLEMENTS[imptype]["PATH"] work msg
        #rbcfg.RUNMSG[imptype]="OK"  #todo stop
        cfgcmd.setCmd(imptype="OK")
        
        self.runner=MapReduceAction.BaseReduceAction(self._basepath, self._imptype)
        self.heartbeat=None
        if(self._imptype in rbcfg.TRAN["HeartBeat"]):
            self.heartbeat=MapReduceAction.HeartBeatAction(self._basepath, self._imptype)
        return
    
    def _run(self):
        #print "_ReduceZipTranDaemon",self._imptype
        _BaseDaemon._run(self)
        self.runner.exe()
        if(self.heartbeat is not None):
            self.heartbeat.exe()
        
        return
    
def MultReduceZipTranDaemon(basepath,imptypes=[],detaSec=datetime.timedelta(seconds=30),delaySec=0):
    return _MultReduceZipTranDaemon(basepath,imptypes,detaSec,delaySec)
    
class _MultReduceZipTranDaemon(_BasePooledDaemon):  
    def __init__(self,basepath,imptypes=[],detaSec=datetime.timedelta(seconds=30),delaySec=0):    
        self._imptypes=[]
        if(type(imptypes) is type([])) :
            self._imptypes=imptypes
        
        _BasePooledDaemon.__init__(self,basepath,None,detaSec,delaySec)
        for imp in self._imptypes:
            cfgcmd.setCmd(imp="OK")
        
        self.runner=MapReduceAction.MultReduceAction(self._basepath, self._imptypes)
        self.heartbeat=None
        
        if(len(rbcfg.TRAN["HeartBeat"])>0):
            self.heartbeat=MapReduceAction.HeartBeatAction(self._basepath, rbcfg.TRAN["HeartBeat"][0])
        return
    
    def _run(self):
        _BaseDaemon._run(self)
        self.runner.exe()
        if(self.heartbeat is not None):
            self.heartbeat.exe()
        
        return

'''
 all imptypes to one ReduceAction 
'''      
reducesf=["onSigle","onMult"]
def ZipTranWorks(basepath,delaySec=0,** detaSec):
    def onSigle(basepath,delaySec=0,** detaSec):
        ret=[]
        for v in rbcfg.IMPLEMENTS:
            if(detaSec is None or not (v in detaSec)):
                ret.append(ReduceZipTranDaemon(basepath,v,None,delaySec))
            else:
                #ret.append(ReduceZipTranDaemon(basepath,v,detaSec[v],delaySec))
                ret.append(ReduceZipTranDaemon(basepath,v,None,delaySec))
            
        return ret
    
    def onMult(basepath,delaySec=0,** detaSec):
        impks=rbcfg.IMPLEMENTS.keys()
        #print "onMult",impks
        return [MultReduceZipTranDaemon(basepath,impks,datetime.timedelta(seconds=30),delaySec)]
    
    f="onSigle"
    if("Reduce" in rbconf._Deamons and rbconf._Deamons["Reduce"] in reducesf):
        f=rbconf._Deamons["Reduce"]
        
    return eval(f)(basepath,delaySec,** detaSec)
    

class _CaptureBaseDaemon(_BasePooledDaemon):  
    def __init__(self,basepath,imptype,detaSec,delaySec=0):    
        if(imptype is None) :
            raise errs.RbErr("error imptype")
        
        _BasePooledDaemon.__init__(self,basepath,imptype,detaSec,delaySec)
        
        return
    
    def _canWork(self):#todo stop        
        self._can=cfgcmd.canWork(self._imptype)
        #wlog.getLogger().debug(str((self._imptype,self._can)))
        return self._can    
    
    def _post(self):
        self._donotify()
        self._posted=True
        return
    
    def _before(self):
        if(self._posted is True):self._posted=False
        ok=self._canWork()  #todo stop
        if(ok==False):
            return ok
        
        self._now=datetime.datetime.now()
        if(self._last is None):
            return ok
        
        dd1=self._now-self._last
        slp=self._dtdelta.seconds-dd1.seconds
        if(slp>0):
           linux.doPrint( "Map Sleep:",slp)
           time.sleep(slp)
        
        return ok
        
        
    
    def _exe(self):
        while True:
            #wlog.getLogger().debug(self._imptype+"_exe"+str(self))
            if(self._stoped==True):
                if(self._posted is False):
                    self._post()
                self._onstoped()  # my carrier is failed,sorry
                cfgcmd.setSts(**{self._imptype:"STOPED"}) 
                continue
            
            if(self._posted is True):self._posted=False
            self._work()
            self._onstoped()
        return 
    
    def _onstoped(self):
       cfgcmd.setSts(**{self._imptype:"READY"}) 
       #if(self._imptype is "BASE"):print self._imptype+":_onstoped:"+str(self);wlog.getLogger().debug(self._imptype+":_onstoped:"+str(self))
       _BasePooledDaemon._onstoped(self)
       
       return

def CaptureMapDaemon(basepath,imptype,detaSec=None,delaySec=0):
    if(imptype is None or not (imptype in rbcfg.IMPLEMENTS)) :
            raise errs.RbErr("error imptype" +imptype)
        
    if(detaSec is None):
        detaSec=datetime.timedelta(seconds=rbcfg.IMPLEMENTS[imptype]["TIMER"])
        
    cls=_CaptureMapDaemon
    if("CAP" in rbcfg.TRAN and rbcfg.TRAN["CAP"] in capdaemons):
        cls=capdaemons[rbcfg.TRAN["CAP"]]
        
    #return   _CaptureMapDaemon(basepath,imptype,detaSec,delaySec)  
    return   cls(basepath,imptype,detaSec,delaySec)  

'''
 one imptype to one CaptureMapDaemon , to one timer
'''    
class _CaptureMapDaemon(_CaptureBaseDaemon):  
    def __init__(self,basepath,imptype,detaSec,delaySec=0):         
        _CaptureBaseDaemon.__init__(self,basepath,imptype,detaSec,delaySec)
        
        #self.dbw=pjbuilder.DBPool.pop(rbcfg.IMPLEMENTS[imptype]["POOL"])
        self.dbw=None
        #print rbpjs.WorkPojos
        #self.runners=MapReduceAction.CaptrueMapActions(rbpjs.WorkPojos[imptype], basepath, self.dbw,imptype)
        self.initRunners()
        '''
        if(imptype in ["REALP","REAL1"]):# real patch is special
            self.runners=MapReduceAction.CaptrueMapActions(rbpjs.pojonames[imptype], basepath, self.dbw,imptype)
        else:
            self.runners=MapReduceAction.CaptrueMapActions(rbpjs.pojonames[imptype], basepath, self.dbw)
        '''    
        return
    
    def initRunners(self):
        self.runners=MapReduceAction.CaptrueMapActions(rbpjs.WorkPojos[self._imptype], self._basepath, self.dbw,self._imptype)
    
    def _run(self):
        _BasePooledDaemon._run(self)
        cfgcmd.setSts(**{self._imptype:"RUNNING"})
        if(self.dbw is None):
            self.dbw =pjbuilder.DBPool.pop(rbcfg.IMPLEMENTS[self._imptype]["POOL"])
        linux.doPrint( self._imptype+".dbw:"+str(self.dbw))
        wlog.getLogger().debug( self._imptype+".dbw:"+str(self.dbw))
        for r in self.runners:
        #     r.exe(self.dbw)
        
            try:
                r.exe(self.dbw)
            except errs.RbDBErr,dbe:
                cfgcmd.setSts(**{self._imptype:"ERRDB"})
                pjbuilder.DBPool.back(self.dbw,rbcfg.IMPLEMENTS[self._imptype]["POOL"],True)
                self.dbw=None
                wlog.doTraceBack()
                return 
            except Exception,err:
                wlog.doTraceBack()
        wlog.getLogger().debug( self._imptype+"RUNNED")
        cfgcmd.setSts(**{self._imptype:"RUNNED"})
        pjbuilder.DBPool.back(self.dbw,rbcfg.IMPLEMENTS[self._imptype]["POOL"])
        self.dbw=None
        return
    
    def _post(self):
        if(self.dbw is not None):
            self.dbw.close()
            self.dbw=None
                
        _CaptureBaseDaemon._post(self)
        return
    
capdaemons["DB"]=_CaptureMapDaemon

class _CaptureFtpDaemon(_CaptureBaseDaemon):  
    def __init__(self,basepath,imptype,detaSec,delaySec=0):         
        _CaptureBaseDaemon.__init__(self,basepath,imptype,detaSec,delaySec)
        #self.runner=MapReduceAction.FTPDownFilesAction(self._basepath, self._imptype)
        self.initRunners()
        
        return
    
    def initRunners(self):
        self.runner=MapReduceAction.FTPDownFilesAction(self._basepath, self._imptype)
    
    def _run(self):
        _BasePooledDaemon._run(self)
        cfgcmd.setSts(**{self._imptype:"RUNNING"})
        
        try:
            self.runner.exe()
            cfgcmd.setSts(**{self._imptype:"RUNNED"})
        except:
            wlog.doTraceBack()
            cfgcmd.setSts(**{self._imptype:"ERRDB"})
        
        return  
    
capdaemons["FTP"]=_CaptureFtpDaemon      
    
'''
all imptypes to one CaptureWorks 
'''      
def CaptureWorks(basepath,delaySec=0,** detaSec):
    ret=[]
    for v in rbcfg.IMPLEMENTS:
        if(detaSec is None or not (v in detaSec)):
            ret.append(CaptureMapDaemon(basepath,v,None,delaySec))
        else:
            ret.append(CaptureMapDaemon(basepath,v,detaSec[v],delaySec))
        
    return ret    

class _MonitorDaemon(_BaseDaemon):
    def __init__(self,dpl,basepath='',imptype=None,detaSec=datetime.timedelta(seconds=0),delaySec=0):
        wp=self._dotimer(basepath) # my carrier is failed,and to reduce monitor thread sorry
        _BaseDaemon.__init__(self, wp, imptype, detaSec, delaySec)
        self.runner=BaseAction.StopedRestartAction(dpl)
        return
    
    def _dotimer(self,basepath):
        if("Monitor" in rbconf._Deamons and rbconf._Deamons["Monitor"]==False):return None
        return basepath
    
    def _work(self): #_run(self):
        self._last=None
        #print '_MonitorDaemon'
        
        self._stoped=self.runner.exe()
        #print self._stoped
        return
    
    def _exe(self):
       _BaseDaemon._exe(self) 
       return
       
    def start(self):
        if(self._timer is None):# my carrier is failed,and to reduce monitor thread sorry
            self.runner.exe()
            return
        
        _BaseDaemon.start(self) 
        return
    
def MonitorRestartDaemon(* arg ):
    return  _MonitorDaemon(*arg)
        