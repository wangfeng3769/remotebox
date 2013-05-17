'''
Created on 2012-3-21

@author: tanglh
after 0.8.7
'''

import datetime,os,sys
import rbcommit.csock as csock
import rbcommit.cmodem as cmodem
import rbruntime.ParseString as RRPS
import rbruntime.dirfile as dfile
import rbruntime.Linux as linux
import rbconf.cfgvol as cfgvol
import rberror.Errors as errs
import rblog.worklog as wlog
import UpgMode as umode

def buildProtocol(ftag):
    return RRPS.dtParse2Str(datetime.datetime.now(),'DateTime21')+ftag

def buildUpgStr(volStr,ftag):
    filename=buildProtocol(ftag)
    #print 'buildUpgStr',volStr,ftag,filename
    return csock.buildRemoteProtocol(cfgvol.upg['headtag'], filename, 10)+volStr

def buildShakehandStr(volStr=cfgvol.getCurVol()):
    '''
    __version__ = "0.8.6"  --->0000000806 if curvol "0.8.6" 
    
    shakehand string:&&&&0000000046RENYDW00082120111108135353625000HAND00000000100000000806
    answer string:100000008070000077606  if next vol "0.8.7"  tar.gz size is 77606  bytes
    answer string:100000000000000000000  if no next vol
    '''
    return buildUpgStr(volStr,"HAND")

def buildDownloadStr(volStr):
    '''
    down  0.8.7  upgrade tar.gz  
    ask to down string:&&&&0000000046RENYDW00082120111108135353625000DOWN00000000100000000807
    down the tar.gz stream
    '''
    return buildUpgStr(volStr,"DOWN")

def buildSuccessStr(volStr):
    '''
    upgrade  0.8.7  ok
    msg string:&&&&0000000046RENYDW00082120111108135353625000SSOK00000000100000000807
    answer string:100000008080000078608  if next vol "0.8.8"  tar.gz size is 78608  bytes
    answer string:100000008070000000000  if no next vol
    '''
    return buildUpgStr(volStr,"SSOK")

def buildFailStr(volStr):
    '''
    upgrade  0.8.7  ok
    msg string:&&&&0000000046RENYDW00082120111108135353625000FAIL00000000100000000807    
    answer string:100000008070000000000  if no next vol
    '''
    return buildUpgStr(volStr,"FAIL")

def begin():    
    cfgvol.persistCfgVol()
    cfgvol.upg['action']={'cur':None,'next':'HAND','times':0}
    cfgvol.upgmsg["request"]={"msg":"","res":None} 
    cfgvol.setUPGState(1)
    return

def stop():
    cfgvol.upg['action']={'cur':None,'next':None,'times':0}
    cfgvol.upgmsg["request"]={"msg":"","res":None}
    cfgvol.upgmsg['curDown']={'vol':None,'size':-1}
    '''
    if(cfgvol.isTime4Upg()):
        cfgvol.setUPGState(2)
    '''
    
    cfgvol.setUPGState(2) #cfgvol.setUPGState(0)
    return

def restart():
    # call sh file to files backup RemoteBox , and combine tars and copy and bash.start
    def startBox():
        linux.remoteBoxUpgRework() #
        return
    
    def startP():
        pass
    
    if(len(cfgvol.upgmsg['downloads'])):
            eval(cfgvol.upg['restart'])()
    
    return

def isWorkTime():
    return False

def commSender(reqStr,** karg):
    return csock.commTranBydtu(reqStr, None)

def downSender(reqStr,readsize,** karg):
    return csock.sizeTranBydtu(reqStr, None, readsize, cfgvol.upg['maxARead'])

def onRcvOK(res):
        if(len(res)<2):
            errs.RbRemoteErr("ERR_RECV")
            
        if(res[0]=="OK"):
            return res[0]
        
        raise errs.RbRemoteErr(res[0])

def commPost(res,** karg):
    def onOK(res):
        return onRcvOK(res)
    
    def onDatas(res):
        result=parseAnswerStr(res[1])
        if(result[0]<>'1'):
            raise errs.RbRemoteErr("ERR_RECV")
        
        return result
    
    def doPost(ok,result=None):
        def doStop4Post():
            cfgvol.upg['action']['next']='STOP' # todo
            #cfgvol.setUPGState(2) # inTime and stop -->down
            
            return 
        
        def onActionTimes():#cfgvol.upg['action']['next']='DOWN'
            ii=0
            if(cfgvol.upg['action']['cur']=='FAIL'):
                return
            
            cfgvol.upg['action']['times']=ii
            return
        
        istime = cfgvol.state4UPG()
        if(ok<>"OK" ):
            # todo report error
            doStop4Post()
            return
        
        if(istime[0]==False or result is None or cfgvol.upg['action']['times']>=cfgvol.upg['maxFTimes']):
            doStop4Post()
            return
        
        if(int(result[1])==0): # after 1.0.0 result[0])==0 result=1,0000000000,0000000000
            cfgvol.upg['action']['next']='DONE' # todo
            #cfgvol.setUPGState(2)
            return
        
        cfgvol.upg['action']['next']='DOWN'
        onActionTimes()# cfgvol.upg['action']['times']=0
        cfgvol.upgmsg['curDown']['vol']=result[1]
        cfgvol.upgmsg['curDown']['size']=int(result[2])
        #cfgvol.setUPGState(1)
        
        return
    
    result=None
    try:
        ok=onOK(res)
        result=onDatas(res)
    except errs.RbRemoteErr,err:
        wlog.doExTraceBack(cfgvol.upg['logtag'])
        ok=err.message
        
    doPost(ok,result)
    
    return

def downPost(res,** karg):   
    def onOK(res):
        try:
           return onRcvOK(res)
        except errs.RbRemoteErr,err:
           wlog.doExTraceBack(cfgvol.upg['logtag'])
           return err.message
        
     
    def getTarFile():
        vol=cfgvol.getCurDown()
        if(vol is None):
            return None
        
        return dfile.joinPath(cfgvol.upg['workpath']['pctar'], vol+umode.filefix["down"])  # todo chk tardir,
    
    def getExdir():
        '''
        vol=cfgvol.getCurDown()
        if(vol is None):
            return None
        
        return dfile.joinPath(cfgvol.upg['workpath']['ptestex'], vol)   # todo chk dir
        '''
        return cfgvol.upg['workpath']['ptestex']
    
    def saveTar(datas=[]):
        tarf=getTarFile()
        if(tarf is None):
            raise "error vol"
        dfile.appendStreamsToFile(tarf, datas)
        return
    
    def extraTar(tarFile,exdir):
        dfile.extar2Dir(tarFile, exdir)
        return
    
    def onDatas(res):        
        try:
            ok=onOK(res)
            datas=res[1]
            saveTar(datas)
            extraTar(getTarFile(),getExdir())
            cfgvol.upgmsg['downloads'].append(cfgvol.upgmsg['curDown']['vol'])
        except :
            wlog.doExTraceBack(cfgvol.upg['logtag'])
            ok="ERR_EXTAR"
            
        #cfgvol.upgmsg['curDown']={'vol':None,'size':-1}
        return ok
    
    def doPost(ok):
        if(ok<>"OK"):
            # report error
            cfgvol.upg['action']['next']='FAIL' # todo
            cfgvol.upg['action']['times']=cfgvol.upg['action']['times']+1
            return
        
        cfgvol.upg['action']['next']='SSOK'
        
        return

    ok=onDatas(res)
    doPost(ok)
    
    return

def parseAnswerStr(datastr):
    if(type(datastr)==type('') and len(datastr)==21):
        ret= [datastr[0],datastr[1:11],datastr[12:]]        
        try:
            int(ret[1])
            int(ret[2])
            
            return ret
        except:
            wlog.getExLogger(cfgvol.upg['logtag']).debug(datastr)
            raise errs.RbRemoteErr("ERR_RECV")
    
    raise errs.RbRemoteErr("ERR_RECV")

actionReg={}

def getUpgAction(atag):
    if(atag in cfgvol.upg['actions'] and atag in actionReg):
        return actionReg[atag]
    
    return None    

class UpgradeBaseAction:
    def __init__(self,action=None):
        self._action=action
        return
    
    def getAction(self):
        return self._action
    
    def getVolStr(self):
        return ''
    
    def getUpgReq(self):
        return None
    
    def getExeArg(self):
        return [self.getUpgReq()]
    
    def getExeKArg(self):
        return {"fsender":self._before(),"fpost":self._post()}
    
    def _before(self):
        return None
    
    def _onWorkTime(self):
        return True
    
    def _doTran(self):
        # csock.dotrans(* self.getExeArg(), ** self.getExeKArg())
        
        if(self._action in cfgvol.upg['actions']):
            cfgvol.upg['action']['cur']=self._action
            
        return 
    
    def exe(self):
        if(self._onWorkTime()==True):
            self._doTran()
            self._done()
        
        return
    
    def _post(self):
        return None
    
    def _done(self):
        cfgvol.persistCfgVol()
        return
    
class UpgradeCommAction(UpgradeBaseAction):
      def _before(self):
        return commSender
      
      def _post(self):
        return commPost
      
      def getUpgReq(self):
        print self.getVolStr(),self.getAction()  # test
        return buildUpgStr(self.getVolStr(),self.getAction())
    
      def _doTran(self):
          UpgradeBaseAction._doTran(self)
          csock.dotrans(* self.getExeArg(), ** self.getExeKArg())
          
          return
    
class _UpgradeHandAction(UpgradeCommAction):
    def __init__(self):
        UpgradeCommAction.__init__(self, 'HAND')
        return
    
    def getVolStr(self):
        return cfgvol.getCurVol()
    
def UpgradeHandAction():
    return _UpgradeHandAction()
actionReg['HAND']=UpgradeHandAction()
    
class _UpgradeSSOKAction(UpgradeCommAction):
    def __init__(self):
        UpgradeCommAction.__init__(self, 'SSOK')
        return
    
    def getVolStr(self):
        return cfgvol.getCurDown()
    
def UpgradeSSOKAction():
    return _UpgradeSSOKAction()
actionReg['SSOK']=UpgradeSSOKAction()
    
class _UpgradeFAILAction(_UpgradeSSOKAction):
    def __init__(self):
        UpgradeCommAction.__init__(self, 'FAIL')
        return
    
def UpgradeFAILAction():
    return _UpgradeFAILAction()
actionReg['FAIL']=UpgradeFAILAction()

class _UpgradeDownAction(UpgradeCommAction):
    def __init__(self):
        UpgradeBaseAction.__init__(self, 'DOWN')
        return
    
    def getExeArg(self):
        return [self.getUpgReq(),cfgvol.upgmsg['curDown']['size']]
    
    def getVolStr(self):
        return cfgvol.getCurDown()
    
    def _before(self):
        return downSender
      
    def _post(self):
        return downPost
    
def UpgradeDownAction():
    return _UpgradeDownAction()
actionReg['DOWN']=UpgradeDownAction()
    
class _UpgradeStopAction(UpgradeBaseAction):
    def __init__(self):
        UpgradeBaseAction.__init__(self, 'STOP')
        return
    
    def _done(self):
        UpgradeBaseAction._done(self)
        stop() 
        
        cfgvol.setUPGState(0) #cfgvol.setUPGState(2) 
        return
    
def UpgradeStopAction():
    return _UpgradeStopAction()
actionReg['STOP']=UpgradeStopAction()
    
class _UpgradeDONEAction(UpgradeBaseAction):
    def __init__(self):
        UpgradeBaseAction.__init__(self, 'DONE')
        return
    
    def _done(self):
        UpgradeBaseAction._done(self)
        stop() 
        
        cfgvol.setUPGState(2) #cfgvol.setUPGState(0)
        restart()
        
        return
    
def UpgradeDONEAction():
    return _UpgradeDONEAction()
actionReg['DONE']=UpgradeDONEAction()
    
class _ScheduleAction:
    def __init__(self):
        self.done()
        
    def nextAction(self):
        actionname= cfgvol.upg['action']['next']
        cfgvol.upg['action']['next']=None
        if(actionname is None):
            return None
        
        action = getUpgAction(actionname)
        if(action is not None):
            cfgvol.upg['action']['cur']=actionname
            
        return action
    
    def done(self):
        self._doing=False
        # cfgvol.setUPGState(2)
        return
    
    def _worked(self):
        action=self.nextAction()
        if(action is not None):
            action.exe()
            
        return action
    
    def exe(self):
        if(self._doing == True):
            return
        
        ok=cfgvol.state4UPG()
        if(ok[0]==False or ok[1]==False ):
            return
        
        begin()
        self._doing=True

        action = self._worked()
        while(action is not None):
            cmodem.doSleep(1)
            action = self._worked()
        
        self.done()
        return
    
_UpgActions={}
def getUpgSchedule(tag=None):
    def ScheduleAction(*arg,**karg):
        return _ScheduleAction(*arg,**karg)
    
    ret=None
    if(type(tag)==type('')):
        if(tag in _UpgActions):
            return _UpgActions[tag]
        
        if(len(_UpgActions.keys())<1):
            _UpgActions[tag]=ScheduleAction()
            return _UpgActions[tag]
    
    return ret 