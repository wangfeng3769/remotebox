'''
Created on 2011-8-5

@author: Tanglh
'''

import webapi

def getWebParaValue(*ks):
    ret={}
    wvs=webapi.input(_unicode=False)
    for k in ks:
        if(k in wvs):
            ret[k]=webapi.input(_unicode=False)[k]
            
    return ret

'''
def BaseCfgCtxGet(* arg,** karg):
    ctx=_BaseCfgCtxComm(getCfgedValues4Pri,WEBNAMETAGS["GET"],* arg,** karg)
    ctx["action"]=dfile.joinPath('/A/', arg[0])
    ctx["mssg"]=""
    
    if("mssg" in karg and karg["mssg"] is not None):
        ctx["mssg"]=karg["mssg"]
    
    ctx["names"]=None    
    if("names" in karg):
        ctx["names"]=karg["names"]
    
    ctx["srcnames"]=[]
    if("srcnames" in karg):
        ctx["srcnames"]=karg["srcnames"]
    elif arg[0] in rbcfg.CONFIGPAGES:
        ctx["srcnames"]=rbcfg.CONFIGPAGES[arg[0]]     
    
    if("values" in karg):   
        ctx["values"]=karg["values"]
    else:  
        ctx["values"]=getCfgedValues4Pri(ctx["srcnames"], ctx["names"],** karg)
        
    if(ctx["names"] is None):
        ctx["names"]=ctx["srcnames"]
        
    ctx["dics"]=rbcfg.CONFIGITEMS
    
    return arg[0],ctx,{}
    
    def BaseCfgCtxPost(* arg,** karg):
    ctx=newCtx(** karg)
    if("btns" not in ctx):
        ctx["btns"]={}
        
    ctx["btns"]["RESET"]=dfile.joinPath('/A/', arg[0])
    ctx["btns"]["OK"]='/TopOK.html'
    
    ctx["mssg"]=""
    if("mssg" in karg and karg["mssg"] is not None):
        ctx["mssg"]=karg["mssg"]
    
    if arg[0] in rbcfg.CONFIGPAGES:
        ctx["names"]=rbcfg.CONFIGPAGES[arg[0]]            
        ctx["values"]=getCfgedValues(* ctx["names"],** karg)
        
    ctx["dics"]=rbcfg.CONFIGITEMS
    
    return arg[0],ctx,{}
'''