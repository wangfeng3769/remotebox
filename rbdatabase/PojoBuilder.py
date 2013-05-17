'''
Created on 2011-6-13

@author: Tanglh
'''


import os,sys,datetime

# after 0.8.5
import rbdatabase
import DBFactory
import rbaction.BaseAction as RBBModel
import rbruntime.ParseString 
import rbruntime.StringUtils
import rbruntime.PoolUtils as poolutils
import rblog.worklog as wlog
import rbconf
import rbconf.conff as rbcfg
import rberror.Errors as errs

class _DBInnerPool(poolutils._InnerPool):
        def _newDB_(self):
            return DBFactory.DBWrapByConn(DBFactory.getConnStringByCfg())
    
        def _releaseDB_(self,ret):
            ret.close()
            #del ret
            ret=None
            return ret

class _DBWrapPool(poolutils._WrapPool):
    def __init__(self,** karg):
        kkr=karg
        
        if 'BASE' not in kkr:kkr['BASE']=1
        if 'ATTEN' not in kkr:kkr['ATTEN']=1
        if 'REAL' not in kkr:kkr['REAL']=10
        if 'REALP' not in kkr:kkr['REALP']=1
        
        poolutils._WrapPool.__init__(self, _DBInnerPool,** kkr)
        
        return
    
def DBWrapPool():
    return _DBWrapPool()

def createFieldsStr(fldns):
    if(fldns is None or len(fldns)<1):
        raise  errs.RbErr("Empty fields!!!")
    
    return rbruntime.StringUtils.pAstr(fldns)

def createQuery(tbn,fldns,wheresub=""):
    if(tbn is None or type(tbn)!=type('') ):
        raise errs.RbErr("error table name!!!")
    
    return "select "+createFieldsStr(fldns)+"  from "+tbn+"  "+wheresub
    
def createDel(tbn,wheresub=""):
    if(tbn is None or type(tbn)!=type('') ):
        raise errs.RbErr("error table name!!!")
    
    return "delete  from "+tbn+"  "+wheresub

def DBCaptrue(tbn,**arg):
    return _DBPojoCaptrue(tbn,**arg)

'''
   1- catch pojos from db
   2- provid pojos page by page  1000pojos per page
   3- del pojos  when all ok
'''
class _DBPojoCaptrue:  #class _DBPojoOPBase(RBBModel._BasePojoOP): 
     def __init__(self,tbn,PAGESIZE=rbcfg.db["PAGESIZE"],** arg): 
         self.tbn=tbn
         self._pojodef=arg
         
         self._pgsize=PAGESIZE
         
         self.pgNo=-1
         
         return
     
     def createQuerySQL(self):
         return  createQuery(self.tbn,self._pojodef["fields"],self.wheresub)
     
     def createDelSQL(self):
         return createDel(self.tbn,self.delsub)
     
     def begin(self,dbw,dbctrl):
         self.delsub=None
         self.wheresub,self.dt1,self.dt2=dbctrl.begin(dbw);
         wlog.getExLogger(rbdatabase.logTag).debug(str((dbctrl,dbctrl.rcd2))) # 1.0.0
         if(self.wheresub is None):
             dbctrl.oked()
             return
         
         ssql=self.createQuerySQL()
         wlog.getExLogger(rbdatabase.logTag).debug(str((dbctrl,ssql,self.dt1,self.dt2)))
         self.rcds=dbw.fetchRs("ALL",ssql,(self.dt1,self.dt2))
         if len(self.rcds)>0:
             wlog.getExLogger(rbdatabase.logTag).debug(self.tbn+":begun() fetch:"+str(len(self.rcds)))
         if(not(self.rcds is None)):
             self.pgNo=0
             #return
         '''
         lc=len(self.rcds)
         if(lc==0):
             self.pgCount=0
         else:
             self.pgCount=len(self.rcds)/self._pgsize +1 #
         
         self.pgNo=0
         '''    
         self.delsub,self.dt1,self.dt2=dbctrl.okDone(self._pojodef["delWhere"])
         
         return
     
     '''
        return None error for captrue
        return [] empty datas
     '''
     def getPojos(self):# return None or return [],
         hasNext=False
         if(self.pgNo<0):
             return None,hasNext
         
         lc=len(self.rcds)
         be=self._pgsize
         if lc>0:
             wlog.getExLogger(rbdatabase.logTag).debug(self.tbn+":getPojos() lc="+str(len(self.rcds))+":be="+str(be))
         if(lc<=self._pgsize):
             be=lc
         else:
             hasNext=True
             
         try:# get cur page
             return self.rcds[:be],hasNext
         finally: # del cur page at once
             del self.rcds[:be]
         
     def delPojos(self,dbw,dbctrl):
         self.pgNo=-1
         if(self.delsub is None or self.rcds is None):
             return  dbctrl.end() 
         
         ssql=self.createDelSQL()
         if(ssql is None):
             return
         #wlog.getLogger().debug(str((ssql,self.dt1,self.dt2)))
         dbw.exe(ssql,(self.dt1,self.dt2))
         dbw.commit()
                  
         return dbctrl.end()    

if __name__ == '__main__':
    pass

DBPool=DBWrapPool()