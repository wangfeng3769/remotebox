'''
Created on 2011-8-29

@author: Tanglh
'''

import os,sys,threading,datetime
import BaseAction,MapReduceAction,Daemons
import rbconf.conff as rbcfg
import rbconf.cfgcmd as cfgcmd
import rbruntime.dirfile as dfile
import rbdatabase.PojoBuilder as pjbuilder
import rbdatabase.Pojos as rbpjs
import rblog.worklog as wlog

class _CommonDaemonPool:
    def __init__(self):
            self._pl=[]
            return
        
    def extend(self,objs=[]):
        self._pl.extend(objs)
        
    def append(self,obj):
        if(obj is None):return
        if(obj in self._pl):return
        
        self._pl.append(obj)
        return
        
    def rm(self,obj):
        if(obj in self._pl):
            self._pl.remove(obj)
            
        return
        
    def pop(self):
        if(len(self._pl)<1):return None
        
        return self._pl.pop()
    
    def clear(self):
        self._pl=[]
        
        return
    
    def all(self):
        return  self._pl
    
    def size(self):
        return len(self._pl)
    
    def included(self,obj):
        return obj in self._pl

def RunningDaemonPool( * arg,**karg):    
    return _CommonDaemonPool()

class _StopingDaemonPool(_CommonDaemonPool):
    def __init__(self):
            _CommonDaemonPool.__init__(self)
            return

class _StopedDaemonPool(_CommonDaemonPool):
    def __init__(self,stopingDaemonPool=None):
        self._stoping=stopingDaemonPool
        #if(type(stopingDaemonPool) is type(self._stoping)):self._stoping=stopingDaemonPool
           
        _CommonDaemonPool.__init__(self)
        
        return
    
    def canRestart(self):
        return True
        '''
        if(self._stoping is None ):return True
        if(self._stoping.size()==0):return True
        
        wlog.getLogger().debug("stoping:-------") 
        wlog.getLogger().debug(str(self._stoping.all())) 
        wlog.getLogger().debug("stoped:-------") 
        wlog.getLogger().debug(str(self.all())) 
        
        return self.size()>=self._stoping.size()
        '''
        
    def beforeRestart(self):
        pass
    
    def postRestart(self):
        self.clear()  #self._pl.clear()
        self._stoping.clear()
        return

    def restart(self):
        #if(self.size()<1):return False
        
        if(self.canRestart() is False):return False
        
        self.beforeRestart()    
        
        wks=self._pl
        if(self.size()<self._stoping.size()):
            wks=self._stoping.all()
        for o in wks:# my carrier is failed,and to reduce monitor thread sorry
            o.start()
        
        self.postRestart()
        
        return True
    
def TranZipStopingDaemonPool( * arg,**karg):   
    return _StopingDaemonPool( * arg,**karg)

def TranZipStopedDaemonPool( * arg,**karg): 
    return _StopedDaemonPool( * arg,**karg)

def CaptureStopingDaemonPool( * arg,**karg):   
    return  _StopingDaemonPool( * arg,**karg)

class _CaptureStopedDaemonPool(_StopedDaemonPool): 
    def __init__(self,stopingDaemonPool=[],dbPool=None):
        _StopedDaemonPool.__init__(self, stopingDaemonPool)
        
        self._dbpool=dbPool
        
        return
    
    def postRestart(self):
        _StopedDaemonPool.postRestart(self)
        wlog.getLogger().debug("postRestart:"+str(self))
        self._dbpool.clear()
        
        return
    
def CaptureStopedDaemonPool( * arg,**karg):   
    return  _CaptureStopedDaemonPool( * arg,**karg)
