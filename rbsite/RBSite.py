'''
Created on 2011-8-3

@author: Tanglh
'''

import re
import rbconf.conff as rbcfg
import site
import rbweb
import rbweb.webapi as weba
import rbruntime.dirfile as dfile
import rbruntime.cmdexe as cmdexe
import rbruntime.Linux as Linux
import rbaction.WorkController as workctrl
import rblog.worklog as wlog

urls=("/","Index","/(.*).htm","SimpleDispatch","/(.*).html","SimpleDispatch",
      "/images/(.*)","PathDispatch","/js/(.*)","PathDispatch","/style/(.*)","PathDispatch",
      "/A/(.*)","AuthDispatch","/R/(.*)","RunnerDispatch","/Login","login")

refs={}

dictPageCtx={}

backendRunner={}
afterCfgCtxFun={}

def regRefs(key,clss):
    if(clss is None): return
    if(key in refs):return
    if(type(key) is type('')):
        refs[key]=clss
    
    return 

def regPageCtx(key,ctxfn):
    if(key in dictPageCtx):return
    if(type(key) is type('')):
        dictPageCtx[key]=ctxfn
        
    return 

def regAfterCfgCtxFun(key,ctxfn):
    if(key in afterCfgCtxFun):return
    if(type(key) is type('')):
        afterCfgCtxFun[key]=ctxfn
        
    return 

def regBackendRunner(key,ctxfn):
    if(key in backendRunner):return
    if(type(key) is type('')):
        backendRunner[key]=ctxfn
        
    return 

def emptyRuner():
    Linux.doPrint( "emptyRuner")
    return

def exeBackendRunner(key):
    f=emptyRuner
    if(key in backendRunner):
        ff=backendRunner[key]
        if(ff is not None): f=ff
    
    return  f()

def rebootRunner():
    def inLinux():
        return Linux.inLinux() 
    
    def rebootLinux():
        Linux.doReboot()
        return
        
    def rebootWin():
        rebootcmd="shutdown -r -t 01"        
        ret=cmdexe.runcmd(rebootcmd)
        
        return
    
    def reboot():
        if(inLinux()):
            rebootLinux()
        else: 
            rebootWin()
            
        return
    
    def rebootP():
        return
    
    def getReboot(* arg):
        f="rebootP"
        if("reboot" in rbcfg.TRAN and rbcfg.TRAN["reboot"] in arg):
            f= rbcfg.TRAN["reboot"]
            
        return f
    
    f=getReboot("rebootP","reboot")
    return eval(f)()
#reboot
regBackendRunner('reboot',rebootRunner)

def freshCfgRunner():
    import rbconf.cfgdb as cfgdb
    cfgdb.freshConfByDB()
    
    return doRender("index")
regBackendRunner('freshCfg',freshCfgRunner)

def doConsoleRender():
    def catchCosoleArg():
        #return ["showSts"],{"auth":rbcfg.WEB["auth"] }
        return rbcfg.CONWEB["arg"],rbcfg.CONWEB["karg"]
    
    arg,karg=catchCosoleArg()
    return eval(rbcfg.CONWEB["render"])(*arg,**karg)#ctxRender(*arg,**karg)

def doStartRunner():
    workctrl.onStart()
    return doConsoleRender()
    #todo page sts 
    
def doStopRunner():
    workctrl.onStop()
    return doConsoleRender()
    #todo page sts
    
regBackendRunner('onStart',doStartRunner)
regBackendRunner('onStop',doStopRunner)
        
def regPageCtxByTpl(key):
    if(key in dictPageCtx):return
    if(key in rbcfg.CONFIGPagePriTpl):
        c=rbcfg.CONFIGPagePriTpl[key]
        if("tpl" in c):
            kt=c["tpl"]
            if(kt in dictPageCtx):
               regPageCtx(key,dictPageCtx[kt]) 
               
    return

def regPageCtx4Tpls():
    for key in rbcfg.CONFIGPagePriTpl:
        regPageCtxByTpl(key)
        
    return 

def getPathInCtx():#'PATH_INFO'
    environ= weba.ctx.environ
    path= dfile.joinPath(rbcfg.WEB["tpls"], environ['PATH_INFO'] )   
    return path 
   
def pathRender(* arg,** karg):
    if("path" in karg):
        path=karg["path"]
    else: 
        path=getPathInCtx()
    #print "static path:" +path   
    return rbcfg.WEB["render"].loadTemplateByPath(path)()     

def doRender(* arg,** karg):
    if(len(arg)<1):
        return doRender("index")
    
    pg=arg[0]
    if(pg is None):
        pg="index"
    
    #print   'doRender'  ,pg
    wlog.getLogger().debug('doRender:'+str(pg))
    return rbcfg.WEB["render"]._template(pg)(* arg[1:],** karg)

def doRenderA(pg,* arg,** karg):
    #print   'doRenderA',pg
    wlog.getLogger().debug('doRenderA:'+str(pg))
    return rbcfg.WEB["renderA"]._template(pg)(* arg,** karg)

def catchCtxFByPage(pg):
    if(pg in dictPageCtx):
        return dictPageCtx[pg]
    
    return dictPageCtx["default"]

def defaultCtx(* arg,** karg):
    pg="Empty"
    if(len(arg)>0 and arg[0] is not None):
        pg=arg[0]
        
    return pg,arg[1:],{}
regPageCtx("default",defaultCtx)
# dictPageCtx["default"]=defaultCtx

def buildCtxByArg(* arg,** karg):
    if(karg is not None and "ctxfun" in karg):
        ctxf=karg.pop("ctxfun")
        if(ctxf is not None):
            return ctxf(* arg,** karg)
        
    if(len(arg)<1):
        return "index",[],karg
    
    pg=arg[0]
    ctxf=catchCtxFByPage(pg)
    if(ctxf is not None):
            return ctxf(* arg,** karg)
        
    return pg,arg[1:],karg

def ctxRender(* arg,** karg):    
    url,needA,nkarg=doAuth(** karg)
    if(url is not None) :
        return  doRender(url)  
    
    pg,narg,nkarg=buildCtxByArg(* arg,** nkarg)
    
    if(needA==False)  :
        return doRender(pg,* narg ,** nkarg) 
    
    return doRenderA(pg,* narg ,** nkarg)

def passAuth():
    return None

def cookieAuth():#"uCkey"
    if("uCkey" in rbcfg.WEB):
        ukey=rbcfg.WEB["uCkey"]
        uv=None
        '''
        try:
            uv=weba.cookies(ukey)[ukey]
        except:
            pass
        '''
        uv=weba.cookies(ukey)[ukey]
        if(uv is None):
            return rbcfg.WEB["authFUrl"]

    return passAuth()

def doAuth(** karg):
    if(karg is None):
        return None,False,karg
    
    if("auth" in karg):
        f=karg.pop("auth")
        if(f is None):
            f=passAuth
        return f(),True,karg
    
    return None,False,karg

def passLogin(* arg):
    return True,""

def chkLogin(* arg):
    return passLogin(* arg)

class Dispatch:
    def GET(self,htm):
        '''
        pg=htm
        if(pg is None):
            pg="index"
        
        return doRender(*[pg])
        '''
        return doRender(htm)
    
    def POST(self,htm):
        return self.GET(htm)
regRefs("SimpleDispatch",Dispatch)    


class RunnerDispatch:
    def GET(self,htm):
        return exeBackendRunner(htm)
    
    def POST(self,htm):
        return self.GET(htm)
regRefs("RunnerDispatch",RunnerDispatch)   

class PathDispatch:
    def GET(self,htm):
        return pathRender(htm)    
regRefs("PathDispatch",PathDispatch)    
    
class CtxDispatch:
    def begin(self,* arg,** karg):
        return arg, karg
    
    def GET(self,* arg):
        narg,nkarg=self.begin(* arg,Method="GET")
        return ctxRender(* narg,** nkarg)
    
    def POST(self,* arg):
        narg,nkarg=self.begin(* arg,Method="POST")
        return ctxRender(* narg,** nkarg)
    
class AuthDispatch(CtxDispatch):
    def begin(self,* arg,** karg):
        if(karg is None):
            karg={}
        
        karg["auth"]=rbcfg.WEB["auth"]    
        return arg,karg  
regRefs("AuthDispatch",AuthDispatch)  
    
class Login:
    def GET(self):
        return ctxRender("login")
    
    def POST(self):
        user=weba.input(_unicode=False)['user']
        psw=weba.input(_unicode=False)['psw']
        ok,mssg=chkLogin(user,psw)
        
        if(ok):
            weba.setcookie('user', user)
            
            return ctxRender("index")
        else:            
            return ctxRender("login",msg=mssg)
regRefs("login",Login)          
        
class  Index:
    def GET(self):
        return doRender("index")
regRefs("Index",Index) 
'''    
class SiteMain:
    def Get(self):
        url=cookieAuth()
        if( url is not None):
           return  doRender(url)
        
        return ctxRender("ctxmain")
'''
rbcfg.WEB["urls"].extend(urls)
rbcfg.WEB["refs"].update(** refs)
#rbcfg.WEB["auth"]=cookieAuth