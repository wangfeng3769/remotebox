'''
Created on 2011-8-3

@author: Tanglh
'''
import rbconf.conff as rbcfg
import rbconf.cfgdb as cfgdb
import rbconf.cfgvol as cfgvol
import rbweb.webapi as weba
import rbweb.webwork as webwork
import rbruntime.dirfile as dfile
import RBSite

#names for web   and srcnames for cfg  #rbcfg.WEB["auth"]=cookieAuth
WEBNAMETAGS={"POST":["names","srcnames"],"GET":["srcnames","names"]}

def getCurUser():
    def returnSa():
        return cfgdb.SA
    
    def returnCookie():
        ukey=rbcfg.WEB["uCkey"]
        return weba.cookies(ukey)[ukey]
    
    if("auth" in rbcfg.WEB):
        import rbsite.RBSite as rbsite
        if(rbcfg.WEB["auth"]==rbsite.cookieAuth):
            return returnCookie()
        
    return returnSa()
    

def LoginCtxPrvider(* arg,** karg):
    ctx={"names":["user","psw"],"msg":"","action":"/Login"}
    if(karg is not None and "msg" in karg):
        ctx["msg"]=karg["msg"]
        
    return arg[0],[ctx],{}
RBSite.regPageCtx('login', LoginCtxPrvider)
#rbsite.RBrbsite.dictPageCtx["login"]=LoginCtxPrvider

def MainFrameCtxPrvider(* arg,** karg):
    ctx={"left":"/A/left","center":"/Empty.html"}
    
    return arg[0],[ctx],{}
RBSite.regPageCtx('main', MainFrameCtxPrvider)
#rbsite.RBrbsite.dictPageCtx["main"]=MainFrameCtxPrvider

def freshCmd(cmdn,cmds,ctx):
    if(cmds is None or ctx is None):
        return cmds
    
    if(cmdn is None or cmdn not in cmds):
        return cmds
    
    c=cmds[cmdn]
    if(c is None or "status" not in c):
        return  cmds
            
    if("target" not in c):
        c["target"]=ctx["target"]
        
    if("url" not in c):
        c["url"]="/A/"+cmdn
    
    cmds[cmdn]=c    
    return cmds
    
def freshCmds(cmdnames,cmds,ctx):
    if(type(cmdnames) is not type([])):
        return cmds
    
    for cn in cmdnames:
        if(type(cn) is type('')):
            cmds=freshCmd(cn,cmds,ctx)
            continue
        
        if(type(cn) is type([])):
            cmds=freshCmds(cn,cmds,ctx)
            
    return cmds

def LeftCmdCtxPrvider(* arg,** karg):
    cmds=rbcfg.CONFIGCMDS.copy()
    ctx={"target":"workFrame"}
    
    ctx["cmdnames"]=cfgdb.configCMDs(getCurUser())
    ctx["cmds"]=freshCmds(ctx["cmdnames"],cmds,ctx)
    
    return arg[0],[ctx],{}
RBSite.regPageCtx('left', LeftCmdCtxPrvider)
RBSite.regPageCtx('Tleft', LeftCmdCtxPrvider)
RBSite.regPageCtx('Tleft0', LeftCmdCtxPrvider)
#rbsite.RBrbsite.dictPageCtx["left"]=LeftCmdCtxPrvider

def RunnerStatus(* arg,** karg):
    ctx={"mssg":""}
    ctx.update(** rbcfg.RUNMSG)
    
    sts,ists=cfgdb.getCfgSTATUS()
    if(ists>=rbcfg.STSBARRIER["AUTORUN"]):ctx["AUTORUN"]="Y"
    
    return arg[0],[ctx],{}
RBSite.regPageCtx('showSts', RunnerStatus)

def newCtx(** karg):# nkarg["ctx"]=ctx
    if("ctx" in karg):
        return karg["ctx"]
    
    return {}

def getValuesComm(f,* ks,** karg):
    if("values" in karg and karg["values"] is not None):
        return  karg["values"]
    else:    
        return f(* ks)

def getCfgedValues(* ks,** karg):
    ret=getValuesComm(cfgdb.getCfgedValues,* ks,** karg)
            
    for k in ks:
        if(k not in ret):
            ret[k]=""
            
    return ret


def getWebParaValues(* ks,** karg):
    return getValuesComm(webwork.getWebParaValue,* ks,** karg)

def getValues4PriComm(f,ksrc,ktag,** karg):
    ret={}
    if(ksrc is None and ktag is None):
        if("values" in karg and karg["values"] is not None):
            return karg["values"] 
        
        return ret
    
    if(ksrc is None):
        return f(* ktag,** karg)
     
    ret= f(* ksrc,** karg)
    if(ktag is None):
        return ret
    
    if("pri" not in karg):
        return ret
    
    nret={}
    i=-1
    while(i<len(ksrc)-1 and i<len(ktag)-1):
        i+=1
        if(ksrc[i] in ret):
          nret[ktag[i]]=ret[ksrc[i]]
          
    return nret

def patchValues(ksrc,ktag,rdic):
    ret={}
    if(type(rdic) is type(ret)):ret=rdic
    
    if(type(ksrc) is not type([])):return ret
    if(type(ktag) is not type([])):return ret
    
    i=-1
    while(i<len(ksrc)-1 and i<len(ktag)-1):
        i+=1
        if(ksrc[i] in ret):
            if(ktag[i] in ret):continue
            
            ret[ktag[i]]=ret[ksrc[i]]
          
    return ret
    
def getCfgedValues4Pri(ksrc,ktag,** karg):
    return getValues4PriComm(getCfgedValues,ksrc,ktag,** karg) 

def getWebParaValues4Pri(ksrc,ktag,** karg):
    return getValues4PriComm(getWebParaValues,ksrc,ktag,** karg)    

def DispathCtxF(g,p,* arg,** karg):
    if('Method' not in karg):
        return g(* arg,** karg)
    
    pst=karg['Method']
    if(pst=="POST"):
        return p(* arg,** karg)
    
    return g(* arg,** karg)

def getPageItemSmp(* arg,** karg):
    pg=arg[0]
    
    snames=rbcfg.CONFIGPAGES[pg]
    import rbruntime.RbUtils as rbutils
    names=rbutils.copyList(snames)
    
    karg["names"]=names
    karg["srcnames"]=snames
    
    karg["tpl"]=pg
    
    return arg, karg 

def getPageItemPri(* arg,** karg):
    pg=arg[0]
    pt=rbcfg.CONFIGPagePriTpl[pg]
    pri=pt["pri"]
    ln=len(pri)
    tpl=pt["tpl"]
    snames=rbcfg.CONFIGPAGES[pg]
    names=[]
    for n in snames:
        nn=n[len(pri):]
        names.append(nn)
        
    karg["pri"]=pri
    karg["tpl"]=tpl
    karg["names"]=names
    karg["srcnames"]=snames
    
    return arg, karg 

def priCtxWithPri(f,* arg,** karg):
    narg,nkarg=f(* arg,** karg)
    
    ctx={}
    for k in ["pri","tpl","names","srcnames"]:
        if(k in nkarg):
           ctx[k]=nkarg[k]
        
    nkarg["ctx"]=ctx
    
    return narg,nkarg

def DispathCtxFWithPri(fpri,g,p,* arg,** karg):
    f=fpri
    if(f is None):
        f=getPageItemSmp
        
    narg,nkarg=priCtxWithPri(f,* arg,** karg)
    
    return DispathCtxF(g,p,* narg,** nkarg)

def _BaseCfgCtxComm(f,nametags,* arg,** karg):
    ctx=newCtx(** karg)
    
    ctx["dics"]=rbcfg.CONFIGITEMS
    
    ctx["mssg"]=""
    if("mssg" in karg and karg["mssg"] is not None):
        ctx["mssg"]=karg["mssg"]
        
    if("Lsnrtag" in karg):ctx["Lsnrtag"]=karg["Lsnrtag"]
        
    ctx[nametags[0]]=None    
    if(nametags[0] in karg):
        ctx[nametags[0]]=karg[nametags[0]]
    
    ctx[nametags[1]]=None
    if(nametags[1] in karg):
        ctx[nametags[1]]=karg[nametags[1]]
        
    if ctx["srcnames"] is None and ctx["names"]is None:
        if arg[0] in rbcfg.CONFIGPAGES:
           ctx["srcnames"]=rbcfg.CONFIGPAGES[arg[0]] 
        else:
           ctx[nametags[1]]=[]         
    
    if("values" in karg):   
        ctx["values"]=karg["values"]
    else:  
        ctx["values"]=f(ctx[nametags[0]], ctx[nametags[1]],** karg) # f(ctx[nametags[1]], ctx[nametags[0]],** karg)
        
    if(ctx[nametags[0]] is None):
        ctx[nametags[0]]=ctx[nametags[1]]
    if(ctx[nametags[1]] is None):
        ctx[nametags[1]]=ctx[nametags[0]]
        
    return ctx

def afterCommCfgCtx(* arg,** karg):
    ctx=karg['ctx']
    pg=arg[0]
    ctx["action"]=dfile.joinPath('/A/', pg)
    
    if("pri" in ctx):
       pg=ctx["tpl"]
    
    return pg,[ctx],{}

def afterCfgCtxUpdateOK(* arg,** karg):
    pg=arg[0]
    if(pg in RBSite.afterCfgCtxFun):
        fs=RBSite.afterCfgCtxFun[pg]
        for f in fs:
            f(* arg,** karg)
                
    return 

def afterCfgCtx(* arg,** karg):
    f=afterCommCfgCtx
    if("afterCfgCtxFun" in karg  and karg["afterCfgCtxFun"] is not None):
        f=karg["afterCfgCtxFun"]
    
    return f(* arg,** karg)

def BaseCfgCtxGet(* arg,** karg):
    ctx=_BaseCfgCtxComm(getCfgedValues4Pri,WEBNAMETAGS["GET"],* arg,** karg)
    karg['ctx']=ctx
    return afterCfgCtx(* arg,** karg)

def BaseCfgCtxPost(* arg,** karg):
    ctx=_BaseCfgCtxComm(getWebParaValues4Pri,WEBNAMETAGS["POST"],* arg,** karg)
    if("pri" in ctx):
        patchValues(ctx["srcnames"],ctx["names"],ctx["values"])
        
    '''
    if("btns" not in ctx):
        ctx["btns"]={}
        
    ctx["btns"]["RESET"]=dfile.joinPath('/A/', arg[0])
    ctx["btns"]["OK"]='/TopOK.html'    
    
    return "OK",[ctx],{}
    '''
    karg['ctx']=ctx
    return afterCfgCtx(* arg,** karg)

def cfgService(ctx):
     return cfgdb.updateCfg(** ctx["values"])

def smpMsgPrv(msg,ctx):
    return msg
 
def cfgServicePost(failF,msgPrv,*arg,** karg):
    if(msgPrv is None):msgPrv=smpMsgPrv
    
    pg,narg,nkarg=BaseCfgCtxPost(* arg,** karg)
    
    ctx=narg[0]    
    msg=cfgService(ctx)
    if(msg=="S_OK"):
       ctx["mssg"]=msgPrv(msg,ctx)
       if("OK_STATE" in karg):#** {cfgdb.STATUSKEY:karg["OK_STATE"]}
           cfgdb.updateCfg(STATUS=karg["OK_STATE"])
           
       if("OK_STATE_FUN" in karg):#** {cfgdb.STATUSKEY:karg["OK_STATE"]}
           f=karg["OK_STATE_FUN"]
           f()
           #cfgdb.updateCfg(STATUS=karg["OK_STATE"])
           
       afterCfgCtxUpdateOK(* arg,** karg)
           
       ctx["POSTOK"]="Y"
       
       return pg,[ctx],{}
        
    nkarg["mssg"]=msgPrv(msg,ctx)
    
    return failF(* arg,** nkarg)

def DevCode(* arg,** karg):    
    return DispathCtxFWithPri(None,DevCodeGet,DevCodePost,* arg,** karg)
RBSite.regPageCtx("DEVCODE", DevCode)

def DevCodeGet(* arg,** karg):
    return BaseCfgCtxGet(* arg,** karg) 

def DevCodePost(* arg,** karg):
    pg,[ctx],nkarg=BaseCfgCtxPost(* arg,** karg)
    
    value=ctx["values"]['DEVCODE']
    msg=cfgdb.cfgDevCode(value)
    if(msg=="S_OK"):
       ctx["mssg"]=msg
       ctx["POSTOK"]="Y"
       return pg,[ctx],{}
        
    nkarg["mssg"]=msg
    
    return DevCodeGet(* arg,** nkarg)  

def LocalCfg(* arg,** karg):
    return DispathCtxFWithPri(None,LocalCfgGet,LocalCfgPost,* arg,** karg)
RBSite.regPageCtx('LOCAL', LocalCfg)

def setLOCREBOOT(ctx):
    if(ctx is None):
        return ctx
    
    ctx["LOCREBOOT"]="N"    
    if('LocalReboot' in rbcfg.TRAN and rbcfg.TRAN['LocalReboot']=="Y"):
        ctx["LOCREBOOT"]="Y"
        ctx["POSTOKF"]="toReboot()"
        
    return ctx

#update after 0.8.7
def LocalCfgGet(* arg,** karg):
    pg,[ctx],nkarg=BaseCfgCtxGet(* arg,** karg)
    
    if('SELECT' not in ctx):
        ctx['SELECT']={}
        
    ctx['SELECT']["LOCAL_CAPTYPE"]=rbcfg.CAPTYPES
    if("values" in ctx and "LOCAL_CAPTYPE" in ctx["values"] and ctx["values"]["LOCAL_CAPTYPE"]==""):
        ctx["values"]["LOCAL_CAPTYPE"]=ctx['SELECT']["LOCAL_CAPTYPE"][0]
    
    ctx=setLOCREBOOT(ctx)
    ctx=cfgvol.cfgvolToCtx(ctx)
    
    return pg,[ctx],nkarg

#update after 0.8.7
def LocalCfgPost(* arg,** karg):  
    if("OK_STATE" not in karg):
        karg["OK_STATE"]="2"
        
    pg,[ctx],nkarg = cfgServicePost(LocalCfgGet,None,* arg,** karg)
    ctx=setLOCREBOOT(ctx)
    ctx=cfgvol.ctxToCfgvol(ctx)
    
    return pg,[ctx],nkarg 

def DataSourceCfg(* arg,** karg):
    return DispathCtxFWithPri(getPageItemPri,DataSourceGet,DataSourcePost,* arg,** karg)
RBSite.regPageCtx('DataSource', DataSourceCfg)

def DataSourceGet(* arg,** karg):
    return BaseCfgCtxGet(* arg,** karg) 

def DataSourcePost(* arg,** karg):  
    if("OK_STATE" not in karg):
        karg["OK_STATE"]="3"
        karg["OK_STATE_FUN"]=cfgdb.disableDeamonRun
        
    return cfgServicePost(DataSourceGet,None,* arg,** karg)  

def ZALsnrCfg(* arg,** karg):
    return DispathCtxFWithPri(getPageItemPri,ZALsnrCfgGet,ZALsnrCfgPost,* arg,** karg)
RBSite.regPageCtx('ZALsnr', ZALsnrCfg)

def ZALsnrCfgGet(* arg,** karg):
    pg=arg[0]
    #print "ZALsnrCfgGet",pg
    if pg in rbcfg.CONFIGCMDS: karg["Lsnrtag"]=rbcfg.CONFIGCMDS[pg]['name']
    return BaseCfgCtxGet(* arg,** karg)

def ZALsnrCfgPost(* arg,** karg):  
    return cfgServicePost(ZALsnrCfgGet,None,* arg,** karg) 

def updateLocalCfgByDB(* arg,** karg):
    return cfgdb.updateLocalCfgByDB()
RBSite.regAfterCfgCtxFun('LOCAL', [updateLocalCfgByDB])

def updateDataSourceByDB(* arg,** karg):
    return cfgdb.updateDataSourceByDB()
RBSite.regAfterCfgCtxFun('DB', [updateDataSourceByDB])