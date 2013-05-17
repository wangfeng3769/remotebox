'''
Created on 2011-6-10

@author: Tanglh
'''

import time,os,sys
import datetime

import rbconf
import rbconf.conff as rbcfg
import rbconf.cfgcmd as cfgcmd
import rbcommit.csock
import rbruntime
import rbruntime.ParseString as RRPS
import rbruntime.dirfile as dfile
import rbruntime.Linux as linux
import rberror.Errors as errs
import rblog.worklog as wlog


fileSuffs=[".W",".F",".R",".D",".tar.gz"] #W--writing  F--writed   R--reading  D--readed  .tar.gz--ziped
OKMSG=["OK","ERR_RECV"]
def getWFileName(bn):
    if(bn is None or type("")!=type(bn)):
        raise errs.RbErr("error file name")
    
    return bn+fileSuffs[0]

def getWFFileName(bn):
    if(bn is None or type("")!=type(bn)):
        raise errs.RbErr("error file name")
    
    return bn+fileSuffs[1]

def getRFileName(bn):
    if(bn is None or type("")!=type(bn)):
        raise errs.RbErr("error file name")
    
    return bn+fileSuffs[2]

def getRDFileName(bn):
    if(bn is None or type("")!=type(bn)):
        raise errs.RbErr("error file name")
    
    return bn+fileSuffs[3]

def getZipFileName(bn):
    if(bn is None or type("")!=type(bn)):
        raise errs.RbErr("error file name")
    
    return bn+fileSuffs[4]

def parseTBN(filename,partenn):
    pass

def ListParse(* arg):
    return _BaseListParse(* arg)

class _BaseListParse:# dataset 2 strlist
     def __init__(self,tbname,datadef):
         if(tbname!=None ):# if(tbname!=None and type(self._tbname)==type(tbname)):
            self._tbname=tbname
            
         #self.datalst=datalst
         self._datadef=datadef
              
     def parse(self,datalst):
         if(self._tbname is None):
           raise errs.RbErr("no table name")
         
         return RRPS.dtParse2Str(datetime.datetime.now(),'DateTime21')+self._tbname,RRPS.listParse2Str(datalst,self._datadef,";")
     
def  StrLstWriteFile(** arg):
      return _BaseStrLstWriteFile(** arg)  
  
class _BaseStrLstWriteFile:#strlist write to file
    def __init__(self,head='',tail=''):
        self.head=head
        self.tail=tail
        return  
    
    def _openF(self,filename):
        return open(filename,'w')
    
    def writeF(self,filename,strlst):   
        if(filename is None ):
            raise errs.RbErr("error file")
        
        ff=self._openF(filename)
        ff.write(self.head)
        
        if(strlst is not None and len(strlst)>0):
            #ff.writelines(strlst[:len(strlst)-1])
            for strr in strlst[:len(strlst)-1]:
                ff.write(strr+"\n")
            ff.write(strlst[len(strlst)-1])        
        
        ff.write(self.tail)
        
        ff.close()
        
        return

class _BasePojoOP: #provider dataset and del dataset
     def __init__(self): 
         pass
     
     def getPojos(self):
         return None
     
     def delPojos(self):
         return True

def FileZipTransAction(* arg):     
    return _BaseFileZipTrans(* arg)

class _BaseFileZipTrans: #read datafile and zip trans
    def __init__(self,filen,path,psw,remoteType):
        self._filen=filen
        self._path=path
        self._psw=psw
        self._rmtType=remoteType
        return
    
    def _mkNames(self):
        self._ffn= getWFFileName(self._filen)
        self._fpfn=dfile.joinPath(self._path, self._ffn)
        
        self._rfn= getRFileName(self._filen)
        self._rpfn= dfile.joinPath(self._path, self._rfn)
        
        self._dfn= getRDFileName(self._filen)
        self._dpfn=dfile.joinPath(self._path, self._dfn)
        
        self._zip= getZipFileName(self._filen)
        self._pzip=dfile.joinPath(self._path, self._zip)
        
        return
    
    def getRemote(self):
        return rbconf.conff.IMPLEMENTS[self._rmtType]["REMOTE"]
    
    def dozipFn(self,fn):
        return rbruntime.dirfile.dozip(0,self._pzip,self._path,fn,self._filen)
    
    def dozip(self):
        isF=dfile.existFile(self._path, self._filen, fileSuffs[1])
        fn=self._ffn
        if(isF==False):fn=self._rfn
        try:
            return rbruntime.dirfile.dozip(0,self._pzip,self._path,fn,self._filen)
        finally:
            if(isF==True):
                dfile.fileRename(self._fpfn, self._rpfn)
    
    def exe(self):
        self._mkNames()
        
        fsize,bsize=self.dozip()
        #todo rename datafile to D
        #dfile.fileRename(self._fpfn, self._rpfn)
        #os.rename(self._fpfn, self._rpfn)
        ok="OK"
        #datestr = "0000"+rbconf.conff.TRAN["code"]+"1"+rbruntime.cmdexe.runcmd("date +%s000")[0:13]+"00"+fsize
        datestr=rbcommit.csock.getRemoteProtocol(self._filen, fsize)
        try:
            tar=open(self._pzip,"rb")        
                    
            ok=rbcommit.csock.transmit(rbcommit.csock.getTranContent(datestr, tar.read()), self.getRemote())
        except: 
            wlog.doTraceBack()
            ok="FAIL_OPENTAR"
        finally:
            tar.close()
        
        self.post(ok)
        
        return
    
    def postcmd(self,ok):
        #rbconf.conff.RUNMSG[self._rmtType]=ok
        if(rbconf.conff.RUNMSG[self._rmtType] is "STOP"):return 
        a=self._rmtType
        cfgcmd.setCmd(**{self._rmtType:ok})
        return
    
    def posterr(self,ok):
        cfgcmd.setErr(**{self._rmtType:ok})
        return
    
    def post(self,ok):
        self.postcmd(ok)
        if(ok in OKMSG):# ok in OKMSG  ok=="OK"
           dfile.fileRename(self._rpfn, self._dpfn) 
           self.posterr("")
        else:
           dfile.fileRename(self._rpfn, self._fpfn) 
           self.posterr(ok)
       
        dfile.delete_file_folder(self._pzip)
        return


def ClearDataFilesAction(* arg,**  warg):
    return _ClearFiles(* arg,**  warg)

def ClearReadedFilesAction(basePath):
    return _ClearFiles(basePath)
    
class _ClearFiles:
    def __init__(self,basePath,patten="*"+fileSuffs[3]):
        self._bpath=basePath
        self._patten=patten
        
        self._times=0
        
        return
    
    def _delFile(self,dpth):
        dodel=rbconf.conff.TRAN["clsDir"]
        if(dodel):
            rbruntime.dirfile.delFile(dpth, self._patten)
        
        return
    
    def _delAPath(self,AIMP):
        pss=AIMP["PATH"]
        if(pss is None):
            return
        
        pth=rbruntime.dirfile.joinPath(self._bpath, pss)
        linux.doPrint("pth=%s   \n  ptn=%s "% (pth,self._patten))
        rbruntime.dirfile.chkCreateDir(pth)
        self._delFile(pth)
        
        return
    
    def _chkAll(self):
       if(self._times<1):
            for im in rbconf.conff.IMPLEMENTS :
                try:
                    self._chk(im)
                except:
                    pass
            
    def _chk(self,AIMP):
        pss=AIMP["PATH"]
        if(pss is None):
            return
        
        rbruntime.dirfile.chkCreateDir(rbruntime.dirfile.joinPath(self._bpath, pss))
        
        return
    
    def exe(self):
        for im in rbconf.conff.IMPLEMENTS :
            try:
                self._delAPath(rbconf.conff.IMPLEMENTS[im])
            except:
                pass
        
        self._times+=1    
        return

class _StopedRestartAction:    
    def __init__(self,dpl): 
        self._dpl=dpl
    
    def exe(self): #exe(self,dpl=None):
        if(self._dpl is None):
            return True
        
        return self._dpl.restart()
    
def StopedRestartAction(dpl):
    return _StopedRestartAction(dpl)

class _HeartBeatAction(_BaseFileZipTrans):
    def __init__(self,remoteType):
        #print "_HeartBeatAction"
        _BaseFileZipTrans.__init__(self, "", "", "", remoteType)
        return
    
    def exe(self):
        ok="OK"
        try:
            ok=rbcommit.csock.transmit(rbcommit.csock.getHeartBeatProtocol(), self.getRemote())
            wlog.getLogger().debug("HeartBeatAction:"+ok)
        except: 
            wlog.doTraceBack()
            ok="FAIL_OPENTAR"
        finally:
            pass
        
        self.post(ok)
        
        return
    
    def post(self,ok):
        self.postcmd(ok)
        if(ok=="OK"):
           self.posterr("")
        else:
           self.posterr(ok)
       
        return

#after 0.8.7    
class _HeartBeatUpgAction(_HeartBeatAction):
    def __init__(self,remoteType):
        #print "_HeartBeatAction"
        _HeartBeatAction.__init__(self, remoteType)
        return
    
    def _exImp(self,ok):
        import rbupgrade.UpgradeAction as upga
        if(ok == "OK"):
            upgaction=upga.getUpgSchedule(self._rmtType)
            if(upgaction is not None):
                upgaction.exe()
        
        return
    
    def exe(self):
        ok="OK"
        try:
            ok=rbcommit.csock.transmit(rbcommit.csock.getHeartBeatProtocol(), self.getRemote())
            wlog.getLogger().debug("HeartBeatAction:"+ok)
        except: 
            wlog.doTraceBack()
            ok="FAIL_OPENTAR"
        finally:
            pass
        
        self.post(ok)
        self._exImp(ok)
        
        return
    
def HeartBeatAction(* arg):     
    #return _HeartBeatAction(* arg)  
    return _HeartBeatUpgAction(* arg)  # after 0.8.7
