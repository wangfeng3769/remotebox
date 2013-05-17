'''
Created on 2011-8-22

@author: Tanglh
'''

import conff

RPTITEMS=["CMD","STS","ERR"]
RUNNINGSTS=["OK","RUNNING","STOPPING","READY","RUNNED"]
DISENLECMD=["DISENLE"]
CANRUNCMD=["OK"]  #CANRUNCMD=["OK","ERR_RECV"]

def commCmd(cmd):
    if(type(cmd) is type('')):
        conff.RUNMSG["COMM"]=cmd
        
    return

def setRunning(key,**karg):
    if(type(key) is not type('')):return
        
    for k in karg:
      if(k =="COMM" ):continue
      if(k in conff.RUNMSG and key in conff.RUNMSG[k] and type(karg[k]) is type('')):
          conff.RUNMSG[k][key]=karg[k]
          
    return 
        

def setCmd(**karg):
    setRunning("CMD",**karg)
    
    return    

def notifyCommCmd():
    cmd=conff.RUNMSG["COMM"]
   
    for k in conff.RUNMSG:
        if(k =="COMM" ):continue
        if(conff.RUNMSG[k]["CMD"] in DISENLECMD  ):continue
        setCmd(**{k:cmd})
        
    return

def setSts(**karg):
    setRunning("STS",**karg)
    
    return    

def setErr(**karg):
    setRunning("ERR",**karg)
    
    return    

def setRunningItem(key,**karg):
    if(key not in conff.RUNMSG or key is  "COMM"):return
    
    for k in karg:
        if(k in RPTITEMS):
            conff.RUNMSG[key][k]=karg[k]
            
    return

def allStoped():
    ret=(conff.RUNMSG["COMM"] is "STOP")
    if(ret is False):return ret
    
    for k in conff.IMPLEMENTS:
        running=conff.RUNMSG[k]["STS"]
        ret= (running not in RUNNINGSTS)
        if(ret is False):return ret
        
    return ret

def canWork(impType):
    ret=(conff.RUNMSG["COMM"]=="OK")
    
    if(impType=="COMM" or impType not in conff.RUNMSG):    return ret
    # CANRUNCMD  ret and conff.RUNMSG[impType]["CMD"] is "OK"
    return ret and (conff.RUNMSG[impType]["CMD"] in CANRUNCMD)