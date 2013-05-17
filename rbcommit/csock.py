'''
Created on 2011-6-1

@author: Tanglh
'''

import socket,traceback

import time,sys,datetime
import rblog.worklog as wlog
import rbconf.conff as conff
import rbruntime.StringUtils as StringUtils
import rbruntime.ParseString as RRPS
import rbruntime.Linux as linux
import cmodem,cdtu

delay=None

def transmit(content,adress):
    '''
    if("os" in conff.TRAN and conff.TRAN["os"]=="test"):
      return pytrans(content,adress)  #pytrans(content,adress)
    '''
    
    rc=content
    if(rc is None):
        rc=""
    '''    
    lmsg="send data len: %s \n content:%s" % (len(rc),rc)
    print lmsg
    '''
    
    if(adress is None):
        return pytrans(rc,adress) 
    
    return eval(conff.TRAN["transmit"])(rc,adress) #socktrans(rc,adress)

def pytrans(content,adress):
    cmodem.doSleep(1)
    return "OK"  

def socktrans(content,adress):
    sock=None;
    rok="OK"
    
    ddelay=cmodem.getDelay()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect(adress)
    except Exception,x:
        wlog.getLogger().error("FAIL_CON remote socket error:"+str(adress))
        wlog.doTraceBack() 
        cmodem.doSleep(10)# ddelay['socket']['recv'] 10
        return "FAIL_CON"
    
    # wlog.getLogger().debug( lmsg ) 
    try:
        sock.setblocking(False)
        r=sock.send(content)   
        #print r     #todo
        
        data=None
        dtimes=0
        while dtimes<ddelay['socket']['times']:    
            dtimes+=1        
            cmodem.doSleep(ddelay['socket']['recv'])  # reduce cpu usage and syn socket
            try:
                data=sock.recv(1024)  
            except Exception,x:
                wlog.getLogger().error("ignor sock.recv:"+str(dtimes))
                wlog.doTraceBack()   
                continue
                
            if(data) :
                break            
              
        if(data is not None and len(data)>0) :
            linux.doPrint( data)
            if(data[0]=='1'):
                rok="OK" 
                wlog.getLogger().debug("send data success:" + data)
            else:
               rok="ERR_RECV" 
               wlog.getLogger().error("ERR_RECV listener error:"+data)    
        else:
          rok=onFAILRECV()  
    except Exception,x:
        wlog.getLogger().error("FAIL_SEND remote listener error:")
        #wlog.doTraceBack()   
        wlog.doTraceBack()
        #return "FAIL_SEND"
        rok="FAIL_SEND" 
    
    sock.close()   
    
    return rok  

def dtutrans(content,adress):
    rok="OK"
    
    ddelay=cmodem.getDelay()
    
    sdtu=None
    try:
        sdtu=cdtu.getDTU()
        sdtu.open()
    except Exception,x:
        wlog.getLogger().error("FAIL_DTU remote dtu error")
        wlog.doTraceBack() 
        cmodem.doSleep(10)# ddelay['socket']['recv'] 10
        return "FAIL_DTU"
    
    # wlog.getLogger().debug( lmsg ) 
    try:
        data=sdtu.workWR(content,cdtu.WDTU["readsize"],ddelay['socket']['recv']) 
        dtimes=1
        while dtimes<ddelay['socket']['times']:  
            if(data) :
                break      
            
            dtimes+=1        
            cmodem.doSleep(ddelay['socket']['recv'])  # reduce cpu usage and syn socket
            try:
                data=sdtu.doRead(cdtu.WDTU["readsize"]) 
            except Exception,x:
                wlog.getLogger().error("ignor sock.recv:"+str(dtimes))
                wlog.doTraceBack()   
                continue
              
        if(data is not None and len(data)>0) :
            #linux.doPrint( data)
            if(data[0]=='1'):
                rok="OK" 
                wlog.getLogger().debug("send data success:" + data)
            else:
               rok="ERR_RECV" 
               wlog.getLogger().error("ERR_RECV listener error:"+data)    
        else:
          	rok=onFAILRECV()  
    except Exception,x:
        wlog.getLogger().error("FAIL_SEND remote listener error:")
        #wlog.doTraceBack()   
        wlog.doTraceBack()
        #return "FAIL_SEND"
        rok="FAIL_SEND" 
    
    sdtu.close()   
    
    return rok  

def buildRemoteProtocol(head,filename,fsize=0):  
    if(filename is None):
        return ""
    
    dh= "$$$$"
    if(head is not None):
        dh=head
        
    flen=fsize+len(filename)+len(conff.TRAN["Locator"])+len(conff.TRAN["DeviceCode"])+len(conff.TRAN["DataFrom"])+10
    
    sfsize=StringUtils.toFixStr(fsize, "0000000000")
    sflen=StringUtils.toFixStr(flen, "0000000000")
    
    return dh+sflen+conff.TRAN["Locator"]+conff.TRAN["DeviceCode"]+conff.TRAN["DataFrom"]+filename+sfsize
    

def getRemoteProtocol(filename,fsize=0):  
    '''
    if(filename is None):
        return ""
    
    flen=fsize+len(filename)+len(conff.TRAN["Locator"])+len(conff.TRAN["DeviceCode"])+len(conff.TRAN["DataFrom"])+10
    
    sfsize=StringUtils.toFixStr(fsize, "0000000000")
    sflen=StringUtils.toFixStr(flen, "0000000000")
    
    return "####"+sflen+conff.TRAN["Locator"]+conff.TRAN["DeviceCode"]+conff.TRAN["DataFrom"]+filename+sfsize
    '''
    
    return buildRemoteProtocol("####",filename,fsize)

def getHeartBeatProtocol():  
    filename=RRPS.dtParse2Str(datetime.datetime.now(),'DateTime21')+'%%%%'
    return buildRemoteProtocol("$$$$",filename)

def getTranContent(proStr,tarf):
    return proStr+tarf

def packTranContent(proStr,tarf):
    pass

def inLinux():
    return linux.inLinux()

def onFAILRECV():
    if(inLinux()):
        wlog.getLogger().error("FAIL_RECV remote listener error in linux")
        return "FAIL_RECV"
    
    wlog.getLogger().error("ignor FAIL_RECV remote listener error in win")
    return "OK"

# after 0.8.6
# arg[0] content
# arg[1] address
# fsender return data
# fpost   retuen "OK"
def dotrans(*arg,** karg):  
    ret=["ERR_FSENDER"]
    if("fsender" not in karg or karg["fsender"] is None) :
        return ret     
    
    result=karg["fsender"](*arg,** karg)
    '''
    if(result[0] <> "OK"):
        return result
    
    data=result[1]
    '''
    return karg["fpost"](result,** karg)
    
def commTranBydtu(content,adress):
    rok=["OK",None]
    
    ddelay=cmodem.getDelay()
    
    sdtu=None
    try:
        sdtu=cdtu.getDTU()
        sdtu.open()
    except Exception,x:
        wlog.getLogger().error("FAIL_DTU remote dtu error")
        wlog.doTraceBack() 
        cmodem.doSleep(10)# ddelay['socket']['recv'] 10
        return ["FAIL_DTU",None]
    
    # wlog.getLogger().debug( lmsg ) 
    try:
        data=sdtu.workWR(content,cdtu.WDTU["readsize"],ddelay['socket']['recv']) 
        dtimes=1
        while dtimes<ddelay['socket']['times']:  
            if(data) :
                break      
            
            dtimes+=1        
            cmodem.doSleep(ddelay['socket']['recv'])  # reduce cpu usage and syn socket
            try:
                data=sdtu.doRead(cdtu.WDTU["readsize"]) 
            except Exception,x:
                wlog.getLogger().error("ignor sock.recv:"+str(dtimes))
                wlog.doTraceBack()   
                continue
            
        rok[1]=data
    except Exception,x:
        wlog.getLogger().error("FAIL_SEND remote listener error:")
        #wlog.doTraceBack()   
        wlog.doTraceBack()
        #return ["FAIL_SEND",None]
        rok[0]="FAIL_SEND" 
    
    sdtu.close()   
    
    return rok  

def sizeTranBydtu(content,adress,readsize,maxARead=1024):
    rok=["OK",None]
    
    ddelay=cmodem.getDelay()
    
    sdtu=None
    try:
        sdtu=cdtu.getDTU()
        sdtu.open()
    except Exception,x:
        wlog.getLogger().error("FAIL_DTU remote dtu error")
        wlog.doTraceBack() 
        cmodem.doSleep(10)# ddelay['socket']['recv'] 10
        return ["FAIL_DTU",None]
    
    # wlog.getLogger().debug( lmsg ) 
    try:
        datas=sdtu.workWmR(content,readsize,ddelay['socket']['recv'],maxARead) 
                    
        rok[1]=datas
    except Exception,x:
        wlog.getLogger().error("FAIL_SEND remote listener error:")
        #wlog.doTraceBack()   
        wlog.doTraceBack()
        #return ["FAIL_SEND",None]
        rok[0]="FAIL_SEND" 
    
    sdtu.close()   
    
    return rok  

def commpost(data,** karg):
       rok=["OK"] 
       if(data is not None and len(data)>0) :
            #linux.doPrint( data)
            if(data[0]=='1'):                
                wlog.getLogger().debug("send data success:" + data)
            else:
               rok=["ERR_RECV"] 
               wlog.getLogger().error("ERR_RECV listener error:"+data)    
       else:
          rok=[onFAILRECV()]
          
       return    rok