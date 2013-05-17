'''
Created on 2011-6-9

@author: Tanglh
'''

import rblog.worklog as wlog

def pAstr(strs,split=None):  
    ret=""
    if(strs is None or len(strs)<1):
        return ret;
  
    rsplit=","
    if(split!=None and type(split)==type(rsplit)):
        rsplit=split
        
    for strr in strs[0:len(strs)-1]:
        #print(ret,strr,rsplit)
        ret=ret+strr+rsplit
        
    ret=ret+strs[len(strs)-1]
    
    return ret

def appendStr(strl,strm,split):
    ret=None
    if((strl is None) or (strm is None) or (split is None)):
      return ret
    
    return strl+split+strm

def join2Strls(strl,strm,split):
    ret=[]
    if((strl is None) or (strm is None)):
      return ret
    
    rsplit=""
    if(split!=None and type(split)==type(rsplit)):
        rsplit=split
    
    for ss in strl:
        if(ss is None ):
          continue
        
        if(type(ss)==type("")):
            try:
              sm=strm[ss]  
            except:
              continue
            
            if(sm is None):
               sm=""
          
            ssm=appendStr(ss,sm,rsplit)
            if(ssm is None):
              continue
          
            ret.append(ssm)
            
    return ret

def join2AStr(strl,strm,splitIn,splitFull):
    return pAstr(join2Strls(strl,strm,splitIn),splitFull)

def toFixStr(value,refStr="0000000000"):
    if(value is None):
        return refStr
    
    strr=str(value)
    if(len(strr)<1):
        return refStr
    
    if(len(strr)<len(refStr)):
        return refStr[:len(refStr)-len(strr)]+strr
    
    return str[len(strr)-len(refStr):]

def joinListHaveFilter(bak ,stype=[type(''),type([])]):
    ret=[]
    if(bak is None or len(bak)<1):
        return ret
    
    for kk in bak:
        if(kk is None):
            continue
        
        if(type(kk) in stype):
            ret.append(kk)
            continue
        
        if(type(kk) is type(())):
            if(len(kk)<1):
                continue
            
            v=kk[0](* kk[1:])
            if(type(v) is type('')):
                ret.append(v)
     
    return ret

def strLst2String(lst=[],sep=','):
    ret=''    
    for v in lst:
        ret=ret+v+sep
        
    return ret[:len(ret)-1]
    