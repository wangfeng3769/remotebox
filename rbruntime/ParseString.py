'''
Created on 2011-6-7

@author: Tanglh
'''
import time
import datetime

import StringUtils
import rblog.worklog as wlog
import rberror.Errors as errs

dtfomatter={'Date0':'%Y%m%d',
            'Date1':'%Y-%m-%d',
            'Time0':'%H%M%S',
            'Time1':'%X',
            'Time2':'%H:%M',
            'DateTime00':'%Y%m%d %X',
            'DateTime01':'%Y%m%d/%X',
            'DateTime10':'%Y-%m-%d %X',
            'DateTime11':'%Y-%m-%d/%X',
            'DateTime20':'%Y%m%d%H%M%S',
            'DateTime21':'%Y%m%d%H%M%S%f',
            'DateTime22':'%Y-%m-%d %H:%M',
            'DateTime23':'%Y%m%d%H%M',
            'DateTime25':'%Y-%m-%d %X.%f'   # after 0.8.6
            }

def noneParse2Str(obj):
    return None

def emptyParse2Str(obj):
    return ""

def simpleParse2Str(obj):
    wlog.getLogger().debug(obj)
    return str(obj)

def patchParse2Str(obj,patch=" "):
    oo=obj
    if(oo is None):
        oo=patch
        
    return str(obj)

def dtParse2Str(dt,fmt):
    rfmt=dtfomatter.get(fmt)
    return dt.strftime(rfmt)

#after 0.8.7
def dt1900():
    return datetime.datetime(1900,1,1)

def dtParse2StrP(dt,fmt):
    adt=dt
    wlog.getLogger().debug('dtParse2StrP:'+str(adt))
    if(adt is None): #dt1900()  patchParse2Str(dt)
        #return patchParse2Str(dt)  
        adt=dt1900()
    wlog.getLogger().debug('dtParse2StrP:'+str(adt))
    return dtParse2Str(adt,fmt)

singleParse={'none':noneParse2Str,'empty':emptyParse2Str,'simple':simpleParse2Str,'simpleP':patchParse2Str,
             'datetime':dtParse2Str,'datetimeP':dtParse2StrP}# after 0.8.7 'datetimeP':dtParse2StrP  'datetime':dtParse2Str

#uodate 0.8.7
def doNone2Str(obj,* arg):
    if((arg is None) or len(arg)<1):
            return ""
    if(arg[0]=='simpleP'):
            return  singleParse['simpleP'](obj)
        
    if(arg[0] in ['datetimeP']):
        ff=singleParse[arg[0]]
        narg=[obj]   
        narg.extend(arg[1:])
        return ff(*narg) 
        
    return ""

def doParse2Str(obj,* arg):
    #print(obj,arg,len(arg))
    
    if(obj is None ):
        return doNone2Str(obj,* arg)
    
    f=singleParse['simple']
    if((arg is None) or len(arg)<1):  # if((arg is None) or len(arg)<1):  if(arg is None): 
       return f(obj)
    
    ff=singleParse[arg[0]]
    if(ff is None):  #if((ff is None) or len(arg)<2):
       return f(obj)
    
    narg=[obj]   
    narg.extend(arg[1:])
    return ff(*narg)

def tupleParse2Strs(rtp,deftp):   
    ret=[]
    if(rtp is None):
        raise errs.RbErr("error input datas")    
    if(deftp is None):
        raise errs.RbErr("error input data defs")    
    
    if(len(rtp) <= len(deftp)):
        i=0
        while i<len(rtp):     
            #print deftp[i]      
            wlog.getLogger().debug("tupleParse2Strs:"+str(i))
            ret.append(doParse2Str(rtp[i],*deftp[i]))
            i=i+1
            
        # todo for ex field after 0.8.7
        return ret
        
    raise errs.RbErr("not match betewn datas and their defs")   

def listParse2Str(lst,deftp,r_split):   
    ret=[]
    
    if(lst is None or deftp is None):
       return ret

    i=0;now1=datetime.datetime.now()   
    #if(len(lst)>0):wlog.getLogger().debug(str(len(lst))+"listParse2Str():"+str(now1))
    for rtp in lst:
       #print(i)       
       i=i+1
       try:
         ss=StringUtils.pAstr(tupleParse2Strs(rtp,deftp),r_split)
         ret.append(ss)
       except :
           wlog.doTraceBack()
           continue       
    #if(len(lst)>0):wlog.getLogger().debug(str(len(lst))+"end_listParse2Str():"+str(now1))
    
    return ret