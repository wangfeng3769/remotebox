'''
Created on 2011-11-17

@author: Tanglh
'''


import rbconf.conff as rbcfg
import rblog.worklog as wlog
import time

delays=[{'socket':{'recv':1,'times':1},'reduceSleep':{'base':10,'sleep':2}},# adjust after 0.8.0 / 0.8.5
        {'socket':{'recv':5,'times':3},'reduceSleep':{'base':10,'sleep':10}},
        {'socket':{'recv':3,'times':1},'reduceSleep':{'base':10,'sleep':5}}]#{'recv':0,'recv_time':1,'file10':0}

#rbcfg.TRAN['modem']=delays[1]

def setModem(num=0):
    n=0
    if(type(num)==type(n) and num<len(delays) ):
        n=num
        
    rbcfg.TRAN['modem']=delays[n]
    return

def getDelay():
    if('modem' not in rbcfg.TRAN or rbcfg.TRAN['modem'] is None):
       setModem()
       
    return rbcfg.TRAN['modem']

def doSleep(sec=0):
    ssec=0
    if(type(sec)==type(ssec) ):
        ssec=sec
    if(ssec>0):
        time.sleep(ssec)
        
    return

def doSleepReduce(num,dprt=False):
    if(type(num)==type(1) ):
        ddelay=getDelay()
        ws=10
        if(type(ddelay['reduceSleep']['base'])==type(ws) and ddelay['reduceSleep']['base']>0):
           ws=ddelay['reduceSleep']['base']
        try:
            if((num % ws)==0):
                doSleep(ddelay['reduceSleep']['sleep'])
                
                if(True==dprt):
                  import rbruntime.Linux as linux
                  linux.doPrint( 'doSleepReduce:',num,ddelay['reduceSleep']['sleep'])
        except:
            wlog.doTraceBack() 
            
    return       
        