'''
Created on 2012-2-24

@author: Administrator
'''

import serial
import cmodem
import rblog.worklog as wlog

SDTU={"port":0,"baudrate":9600,"timeout":30}
WDTU={"DTU":"SimpleDTU","delay":3,"readsize":21}

class CDTU:
    def __init__(self,* arg ,** karg):
        self.ser=None
        self.working=False
        self.closed=True
        self.port=None
        self._first=True
        
        self._1opened=[]
        self.opened=[]
        
        self.ser=self.buildSer(* arg ,** karg)
        
        if(self.ser.port is None):
            self.ser.port=SDTU["port"]
        self.port=self.ser.port
        self.ser.baudrate=SDTU["baudrate"]
        self.ser.timeout=SDTU["timeout"]
        
        return
        
    def buildSer(self,* arg ,** karg):
        raise "error in build ---  CDTU"
        
    def close(self):
        self.ser.close()
        self.closed=True
        
        return 
    
    def open(self):        
        self.close()
        self.ser.open()
        return self._postOpen()
    
    def getSer(self):
        return self.ser
    
    def _postOpen(self):
        if(self.ser.isOpen()):
            if(self._first == True):
                self.works(self._1opened)
                self._first=False
                
            self.works(self.opened)        
        
        self.ser.flushInput()
        self.ser.flushOutput() #clear buffer
        
        self.closed=False
        return "S_OK"
    
    def write(self,content):
        return self.ser.write(content)
    
    def read(self,size):
        return self.ser.read(size)
    
    def readline(self):
        return self.ser.readline()
    
    def doRead(self,readsize=None):
        if(type(readsize)==type(1)):
           return self.read(readsize)
        
        return self.readline()
    
    def work(self,content,waitsec=1):
        self.write(content)
        cmodem.doSleep(waitsec)
        data= self.readline()
        #print "work" , data
        wlog.getLogger().debug("CDTU work  readed:" +str(data))
        return data
    
    def workWR(self,content,readsize,waitsec=1):
        # after 0.8.5
        cpr=str(content)
        wlog.getLogger().debug("CDTU workWR  towrite :" +cpr[0:60])
        self.write(content)
        cmodem.doSleep(waitsec)
        
        data= self.doRead(readsize)
        #print "work" , data
        wlog.getLogger().debug(str(len(data))+" bytes--CDTU workWR  readed:" +str(data))
        return data
    
    def workWmR(self,content,readsize,waitsec=1,maxARead=1024):
        # after 0.8.6
        if(maxARead<1):
            return [self.workWR(content, readsize, waitsec)]
        
        cpr=str(content)
        wlog.getLogger().debug("CDTU workWmR  towrite :" +cpr[0:60])
        self.write(content)
        cmodem.doSleep(waitsec)
        
        datas=[]
        worksize=readsize
        cworksize=min(worksize,maxARead)
        while(worksize>0):
            data= self.doRead(cworksize)
            wlog.getLogger().debug(str(len(data))+" bytes--CDTU workWmR  readed:"  +str(data)[:21])
            if(data is None):
                cmodem.doSleep(waitsec)
                data= self.doRead(cworksize)
                
            if(data is None):
                break
            
            datas.append(data)
            worksize=worksize-cworksize
        
        if(worksize>0):
            raise "error rcv"    
        
        return datas
    
    def works(self,contents,waitsec=1):
        wks=[]
        if(type(contents)==type(wks)):
            wks=contents
            
        for c in wks:
            if(type(c)==type([]) and len(c)==2):
                self.workWR(c[0],c[1],waitsec)
                continue
                
            self.work(c, waitsec)
            
        return
    
class SimpleDTU(CDTU): #  
    def __init__(self,* arg ,** karg):
        CDTU.__init__(self,* arg ,** karg)
        return 
    
    def buildSer(self,* arg ,** karg):
        return  serial.Serial(* arg,** karg)
    
class JYDTU(SimpleDTU): #  juyingele
    def __init__(self,* arg ,** karg):
        SimpleDTU.__init__(self,* arg ,** karg)
        return 
    
    def buildSer(self,* arg ,** karg):
        #self._1opened=["AT+DEBUG=0",1]
        #self.opened=["AT+TEST=%S4@\n",None]
        return  SimpleDTU.buildSer(self,* arg,** karg)
    
ser=None

def getDTU():
    global ser
    if(ser is None):
       ser= eval(WDTU["DTU"])()
       
    return ser