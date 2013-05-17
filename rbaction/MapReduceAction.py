'''
Created on 2011-6-15

@author: Tanglh
'''

import os,sys,datetime,glob,time

import BaseAction
import rbruntime.dirfile as dirf
import rbconf.conff as conff
import rblog.worklog as wlog
import rberror.Errors as errs
# after 0.8.5
import rbdatabase
import rbftp.FTPWrap as ftpw
import rbcommit.cmodem as cmodem

def getPojoDef(tbn):
    try:
        if(tbn in rbdatabase.Pojos.pojos) :
            return rbdatabase.Pojos.pojos[tbn]
    except Exception ,err:
        wlog.getLogger().error(err)
        
    return None

def CaptrueMapAction(tbn,basepath,dbw,impltype):
    was=getPojoDef(tbn)
    if(was is None):
        return None
    
    return _BaseMapAction(tbn,basepath,dbw,impltype,** was)

def CaptrueMapActions(tbns,basepath,dbw,impltype=None):#tbns=[],basepath,dbw
    ret=[]
    for v in tbns:
        cma=CaptrueMapAction(v,basepath,dbw,impltype)
        if(not (cma is None)):
            ret.append(cma)
            
    return ret

'''
   one table one MapAction get data from interface db and save local files
   include dbwrap(set in)/DBCTRL/DBPojoCaptrue/ListParse/StrLstWriteFile classes
'''
class _BaseMapAction:
     def __init__(self,tbn,basepath,dbw,impltype,** arg):
         self._tbn=tbn
         self._basepath=basepath
         
         self._imp=impltype
         self._dbw=dbw
         self._wkarg=arg
         
         self._initObjs()
         
         return
     
     def getCtrlDef(self):
        if(self._imp==self._wkarg["ctrlc"]):
            return rbdatabase.Pojos.ctrlDef[self._imp]
            
        if(self._imp in rbdatabase.Pojos.specialCtrlDefName) :
            return rbdatabase.Pojos.ctrlDef[rbdatabase.Pojos.specialCtrlDefName[self._imp]]
        
        return rbdatabase.Pojos.ctrlDef[self._wkarg["ctrlc"]]
     
     def _initObjs(self):
         a=None
         if("file" in self._wkarg):
             a=self._wkarg["file"] 
             
         if(a is None):
             self._wkarg["file"]=self._tbn
            
         if("delWhere" not in self._wkarg):
            self._wkarg["delWhere"] =None
         
         if(self._imp is None)    :
             self._imp=self._wkarg["ctrlc"]
             
         self._wkpath=dirf.joinPath(self._basepath, conff.IMPLEMENTS[self._imp]["PATH"])
             
         fs=self.getCtrlDef()  #rbdatabase.Pojos.ctrlDef[self._wkarg["ctrlc"]] #  fs=rbdatabase.Pojos.ctrlDef[self._imp]
         
         self._ctrl=fs["ctrl"](self._dbw,self._tbn,self._wkarg["dtfield"])   #todo
         self._pjCaptrue=fs["pjcap"](self._tbn,PAGESIZE=conff.db["PAGESIZE"],** self._wkarg)  #todo fs["pjcap"](self._tbn,** self._wkarg)
         self._lstParse=fs["lstp"](self._wkarg["file"],self._wkarg["fieldsdef"])#todo
         self._wFile=fs["wfile"]()#todo
         
         return
     
     def _mkFileNames(self,fname):
         self._wf=BaseAction.getWFileName(fname)
     
     def _doPWF(self,pjs):
         if len(pjs)>0:
             wlog.getLogger().debug(self._imp+":"+self._tbn+"_doPWF()="+str(len(pjs)))
             pass
         fname,strl=self._lstParse.parse(pjs)
         
         wf=self._wkpath+BaseAction.getWFileName(fname)
         wff=self._wkpath+BaseAction.getWFFileName(fname)
         if len(pjs)>0:
             ##wlog.getLogger().debug(str(self._ctrl)+":"+self._tbn+":"+wf+"_doPWF()="+str(len(strl)))
             pass
         self._wFile.writeF(wf,strl)
         
         os.rename(wf, wff)
         return 
     
     def exe(self,dbw=None): #todo 0901
         if(dbw is not None): self._dbw=dbw
         nowT=datetime.datetime.now()
         ##wlog.getLogger().debug(self._imp+":exe()"+str(nowT))
         self._pjCaptrue.begin(self._dbw,self._ctrl)
         
         lmsg= self._imp+"_pjCaptrue.begun:"+str(nowT)   
         wlog.getLogger().debug(lmsg)
         wlog.getExLogger(rbdatabase.logTag).debug(lmsg)
         hasNext=True
         while hasNext==True:
                 pjs,hasNext=self._pjCaptrue.getPojos()
                 if(pjs is None or len(pjs)<1):
                    break
                 
                 self._doPWF(pjs)
                 pjs=[]  
                 cmodem.doSleep(1) # reduce cpu usage
         self._post()
             
         return
     
     def _post(self):
         self._pjCaptrue.delPojos(self._dbw,self._ctrl)
         self._ctrl.reset()
         self._dbw=None #todo 0901
         
         lmsg= self._imp+"_post()"+self._tbn+""
         wlog.getLogger().debug(lmsg)
         wlog.getExLogger(rbdatabase.logTag).debug(lmsg)
         return 
     
def BaseReduceAction(basepath,implName):
    return _BaseReduceAction(basepath,implName)

def HeartBeatAction(basepath,implName):
    return BaseAction.HeartBeatAction(implName)

def MultReduceAction(basepath,implNames):
    return _MultBaseReduceAction(basepath,implNames)

def MultReduceHeartBeatAction(basepath,implNames,heartbeatImps):#todo 20111107
    return _MultBaseReduceAction(basepath,implNames)

'''
   one impltype to one ReduceAction
   scan paths for .F file,than tar and del
'''
class _BaseReduceAction:
    def __init__(self,basepath,implType):
        self._bpath=basepath
        self._implType=implType
        #self.refc=arg
        
        return
    
    def getMainFileName(self,fn):
        l=len(fn)
        return fn[:l-2]
    
    def _doexe(self,wkpath,filen):
           mfn=self.getMainFileName(filen)
           wk=BaseAction.FileZipTransAction(mfn,wkpath,conff.TRAN["psw"],self._implType,)
           
           try:
               wk.exe()
               return
           except Exception,err:
               wlog.getLogger().error("ReduceAction error:"+err.message)
               wlog.doTraceBack()
               # other parse
           finally:
               wk=None  
               
    def _exe4Path(self,wkpath,ptn):
        flc=1  #dirf
        for v in dirf.ascFilesByTime(wkpath, glob.glob1(wkpath,ptn)):    # modify 0.8.6       
           self._doexe(wkpath,v)
           flc+=1
           cmodem.doSleepReduce(flc,True) #if(flc%10==0):time.sleep(10)
           
        return 
               
    def exe(self): 
       wkpath=dirf.joinPath(self._bpath, conff.IMPLEMENTS[self._implType]["PATH"])
       
       dirf.delFile(wkpath, "*"+BaseAction.fileSuffs[4])
       
       self._exe4Path(wkpath, "*"+BaseAction.fileSuffs[2])
       self._exe4Path(wkpath, "*"+BaseAction.fileSuffs[1])
       '''
       for v in glob.glob1(wkpath,"*"+BaseAction.fileSuffs[2]):           
           self._doexe(wkpath,v)
           if
       flc=1    
       for v in glob.glob1(wkpath,"*"+BaseAction.fileSuffs[1]):
           self._doexe(wkpath,v)
       '''    
       return
               
'''
   one impltype to one ReduceAction
   scan paths for .F file,than tar and del
'''
class _MultBaseReduceAction:  
     def __init__(self,basepath,implTypes=[]):
        self._bpath=basepath
        self._implTypes=implTypes
        self._reduceActions=[]
        for imp in self._implTypes:
            self._reduceActions.append(BaseReduceAction(self._bpath,imp))
        return
     
     def exe(self): 
         for ra in  self._reduceActions   :
             ra.exe()
             
         return 
     
class _MultReduceHeartBeatAction(_MultBaseReduceAction):  
     def __init__(self,basepath,implTypes=[],heartBeatImps=[]):
        _MultBaseReduceAction.__init__(self, basepath, implTypes)
        
        for imp in self.heartBeatImps:
            self._reduceActions.append(HeartBeatAction(basepath,imp))
        return
               
def FTPDownFilesAction(basePath,imptype):
    return _FTPDownFilesAction(basePath,imptype)
    
class _FTPDownFilesAction:
    def __init__(self,basePath,imptype):
        self._basePath=basePath
        self._imptype=imptype
        self._wkpath=None
        self._ftpdir=None
        
        if([self._implName] in conff.IMPLEMENTS[self._implName]):
            self._wkpath=conff.IMPLEMENTS[self._implName]["PATH"]            
            if("FTPPATH" in conff.IMPLEMENTS[self._implName]):
                self._ftpdir=conff.IMPLEMENTS[self._implName]["FTPPATH"]
            
        return
    
    def exe(self):
        if(self._ftpdir is None or self._wkpath is None):return
        
        oftp=None
        back=False
        try:
            oftp=ftpw.FTPPool.pop(self._imptype)
            ##wlog.getLogger().debug("do ftp:"+self._ftpdir)
            
            oftp.cwd(self._ftpdir)
            self.ftpDowns(oftp, self._ftpdir, self._wkpath, BaseAction.getWFileName, BaseAction.getWFFileName)
            
            return
        except:
            wlog.doTraceBack()
            back=True
            raise errs.RbFtpErr("error work for ftp") 
        finally:    
            ftpw.FTPPool.back(oftp, self._imptype, back)
            oftp=None
    
    def ftpDowns(self,oftp,ftpdir,wkpath,funW,funF):
        if(oftp is None or funW is None or funF is None):return
        
        bn=dirf.joinPath(wkpath, ftpdir)
        
        ftpfs=[]
        try:
            ftpfs=oftp.nlst()
        except:
            wlog.doTraceBack()
            raise errs.RbFtpErr("error get ftp files")
        
        for ftpf in ftpfs:
            if(ftpw.ignorFile(ftpf) or ftpw.existFile(ftpf,wkpath)):continue
            localW=funW(bn)
            localF=funF(bn)
            
            try:
                ##wlog.getLogger().debug("from ftp:"+ftpf)
                ftpw.downFile(oftp,ftpf,localW)
                ##wlog.getLogger().debug("ftp ok:"+localW)
            except:
                wlog.doTraceBack()
                continue
            
            try:
                ftpw.delFile(oftp,ftpf)
            except:
                wlog.doTraceBack()
                continue
            
            dirf.fileRename(localW, localF)
            
        return
              