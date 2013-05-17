'''
Created on 2011-8-19

@author: Tanglh
'''

import rberror.Errors as errs
import rblog.worklog as wlog

class _InnerPool:
        def __init__(self,max=1):
            self._max=max
            self._pl=[]
            self._rcd=0
            return

        def _newDB_(self):
            pass
    
        def _releaseDB_(self,ret):
            pass
        
        def dpop(self):
            if(self._rcd<self._max ):
                if(len(self._pl)<1):
                    self._pl.append(self._newDB_())
                    
                ret=self._pl.pop()
                self._rcd=self._rcd+1
                
                return ret
            
            raise errs.RbErr("FUll") 
       
        def dback(self,ret,release=False):
           if(ret is None):return ret
           if(self._rcd>0):
               if(self._rcd<(self._max+1) and release is False):
                  self._pl.append(ret)
               else:
                  ret= self._releaseDB_(ret)
                   
               self._rcd=self._rcd-1
               return ret
               
           #self._pl.append(ret) 
           ret= self._releaseDB_(ret)
               
           return ret
       
        def clear(self):
            for db in self._pl:
                try:
                    self._releaseDB_(db)
                except:
                    wlog.doTraceBack()
                
            self._pl=[]
            self._rcd=0
            return

class _WrapPool:
    def __init__(self,poolType,** karg):
        self._poolType=poolType
        self._pool={}
        '''
        self._pool={'BASE':_InnerPool(),
                    'ATTEN':_InnerPool(),
                    'REAL':_InnerPool(10),
                    'REALP':_InnerPool()}
        '''
        for v in karg:
            self.initPool(v,karg[v])
            
        return
    
    def initPool(self, name, value):
        rv=1
        if(type(value)==type(1) and value>0):
            rv=value
            
        self._pool[name]=self._poolType(rv) #eval(self._poolType)(rv)
        
        return
        
    def pop(self,type='BASE'):
        return self._pool[type].dpop()
    
    def back(self,ret,type='BASE',release=False):
        if(type in self._pool):
          return self._pool[type].dback(ret,release)
        
        return None
    
    def clear(self,type=None):
        if(type in self._pool):
            self._pool[type].clear()
            return
        
        if(type is not None):return
        
        for t in self._pool:
            self._pool[t].clear()