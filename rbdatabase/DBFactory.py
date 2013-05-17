'''
Created on 2011-6-9

@author: Tanglh
'''

import os,sys,datetime
import pyodbc

# after 0.8.5
import rbdatabase

import rbruntime
import rbruntime.StringUtils
import rbruntime.Linux as linux

import rbconf
import rbconf.conff as rbCfg
import rblog.worklog as wlog
import rberror.Errors as errs

connperpn={"win":["DRIVER","SERVER","PORT","DATABASE","UID","PWD"],"linux":["DRIVER","SERVERNAME","DATABASE","UID","PWD"]}
connpsplit=";"
conneqsplit="="

drivern="DRIVER"
defaultDrv="{SQL Server}"

deltasec=datetime.timedelta(seconds=1)
deltasec10=datetime.timedelta(seconds=10)

'''
CREATE TABLE CTRLB1(
    ID varchar(38) NOT NULL DEFAULT (newid()),
    CTD datetime NOT NULL DEFAULT (getdate()),
    LTD datetime ,
    STATUS smallint NOT NULL DEFAULT ((0)),
    PRIMARY KEY (ID)
);
CREATE TABLE CTRLR1(
    ID varchar(38) NOT NULL DEFAULT (newid()),
    CTD datetime NOT NULL DEFAULT (getdate()),
    LTD datetime ,
    DTD datetime ,
    STATUS smallint NOT NULL DEFAULT ((0)),
    PRIMARY KEY (ID)
);
'''
BaseCtrlType={"FLDS":["ID","CTD","LTD","STATUS"],
              "CREATE":"""
                       CREATE TABLE %s (
                        ID varchar(38) NOT NULL DEFAULT (newid()),
                        CTD datetime NOT NULL DEFAULT (getdate()),
                        LTD datetime ,
                        STATUS smallint NOT NULL DEFAULT ((0)),
                        PRIMARY KEY (ID)
                    )""",
              "CHK":"SELECT 1 FROM sysobjects WHERE type = 'U' AND name = '%s'"
              }
RealCtrlType={"FLDS":["ID","CTD","LTD","DTD","STATUS"],
              "CREATE":"""
                       CREATE TABLE %s (
                        ID varchar(38) NOT NULL DEFAULT (newid()),
                        CTD datetime NOT NULL DEFAULT (getdate()),
                        LTD datetime ,
                        DTD datetime ,
                        STATUS smallint NOT NULL DEFAULT ((0)),
                        PRIMARY KEY (ID)
                    )""",
              "CHK":"SELECT 1 FROM sysobjects WHERE type = 'U' AND name = '%s'"
              }

CtrlTypes={"BASE":BaseCtrlType,"REAL":RealCtrlType}

def getConnString(DRIVER=defaultDrv,PWD="",** args):
    return _getConnString(DRIVER=defaultDrv,PWD="",** args)

def _getConnString(** args):
    vls={}
    try:
        vls=args.copy()
    finally:
        pass
    
    if(not vls.has_key(drivern) or vls[drivern] is None):
          vls[drivern]= defaultDrv 
    
    ks=connperpn["win"]
    if(linux.inLinux()):ks=connperpn["linux"]
    return rbruntime.StringUtils.join2AStr(ks, vls, conneqsplit, connpsplit)#(connperpn, vls, conneqsplit, connpsplit)

def getConnStringByCfg():
    return _getConnString(** rbCfg.db)

def _curexe(curs,* arg):
    try:
        curs.execute(* arg)
    except: 
        emsg="error_curexe()"+str(arg)
        wlog.getExLogger(rbdatabase.logTag).debug(emsg)
        wlog.doExTraceBack(rbdatabase.logTag)
        raise errs.RbDBErr(emsg)

def _fetchAll(curs,* arg):
    #wlog.getLogger().debug("_fetchAll"+str(arg))
    _curexe(curs,* arg)
    #wlog.getLogger().debug("_fetchAll_curexe"+str(arg))
    try:
        return curs.fetchall()
    finally:
        #wlog.getLogger().debug("end_fetchAll"+str(arg))
        pass

def _fetchOne(curs,* arg):
    _curexe(curs,* arg)
    return curs.fetchone()

# chech table  is exist otherwise create it
def chkCreateTable(dbw, ** sqls):
    '''
    try:
        ret = dbw.fetchRs("ONE", sqls["CHK"]) #ret = dbw.fetchRs(model="ONE",* sqls["CHK"])
    except:
        wlog.doTraceBack()
        raise errs.RbDBErr('err db conn')
    '''
    ret = dbw.fetchRs("ONE", sqls["CHK"]) 
    if(ret is None or len(ret)<1):
        dbw.exe(sqls["CREATE"])
        dbw.commit()
        
    return

def DBWrap(** args):
    return _DBWrap(getConnString(** args))

def DBWrapByConn(connstring):
    #print "connstring:"+connstring
    return _DBWrap(connstring)

fetchModels={"ONE":_fetchOne,"MANY":_fetchAll,"ALL":_fetchAll}

class _DBWrap:  
    def __init__(self,connstring):
        self._connstring=connstring
        self._isClose=True
        
        self.curs=None
        self.conn=None
        
    def _open(self):
        if((self.conn is None) or  (self._isClose==True) ):
            linux.doPrint( "self._connstring:"+self._connstring)
            self.conn=pyodbc.connect(self._connstring)
            self._isClose=False
            
        return self.conn
    
    def _cursor(self):
        if(self.curs is None):
            self.curs=self._open().cursor()
            
        return self.curs
    
    def fetchRs(self, model="ALL", * arg  ):
        #print arg[0]
        return fetchModels[model](self._cursor(),* arg)
    
    def exe(self, * arg):
        #print arg
        _curexe(self._cursor(),* arg)
        
    def commit(self):
        self.conn.commit()
        
    def rollback(self):
        self.conn.rollback()
    
    def close(self):
        #print str(self)+":"+str(self._isClose)
        if self.curs is not None:
            self.curs.close()
            self.curs=None
        if self.conn is not None:
            self.conn.close()
            self.conn=None
        self._isClose=True 
        
        return
    
def createEmptyCtrlRcd(fields):
    ret={}
    
    if(fields is None):
       return None    
    
    for ss in fields:
        ret[ss]=None
        
    return ret;

def setCtrlRcd(fields,value,ret=None):
    if(value is None ):
        return None
    
    if(ret is None):
        ret=createEmptyCtrlRcd(fields)
    
    for i in range(len(fields))  :
        if(i<len(value)):
            ret[fields[i]]=value[i]
            
        # break
    
    return ret
        
    
class _CtrlTB: 
    def __init__(self,dbw,tbname,dtfield):
        self._head=rbCfg.getCtrlHead()  #"ZA_CTRL_"
        self.ok=False
        self.flow=["None","Checked","Begun","Ok","Ended"]
        self.step=0
        self.dbw=dbw   #  _DBWrap instance
        self.tbn=tbname # tablename
        self._inToryishe=inToryishes(self.tbn)
       
        self.dtfield=dtfield  # the contralled tbl's datetime field name
        self.ctrlType=None
        self.fields=None
        #self.rcd1={}
        #self.rcd2={}
        return
    
    def _setTbn(self):
        self._head=rbCfg.getCtrlHead() #1.0.0.1
        wlog.getExLogger(rbdatabase.logTag).debug("setTbn_head:"+self._head+"_tbn:"+self.tbn)
        
        if(self.tbn.startswith(self._head)):return
        if(self.tbn.startswith(self._head)):return  # fore
        self.tbn=self._head+self.tbn
        
        return           
        
    def check(self,dbw=None):
        if(dbw is not None):self.dbw=dbw
        if(self.step>0):
           return
       
        if(self.tbn is None or type(self.tbn)!=type("")):
            raise  errs.RbErr("error table to be controlled")
        
        if(self.dtfield is None or type(self.dtfield)!=type("")):
            raise  errs.RbErr("error field of the table to be controlled")
        
        if(self.dbw is None): # todo0901
            raise  errs.RbErr("error dbwrap")
        
        self._setTbn()
        self._init()
        '''
        try:
            self._init()
        except:
            wlog.doTraceBack()
        '''
        self.step=1
        
        return
    
    def reset(self):
        self.step=1
        self.dbw=None
        return 
        
    def _init(self):
        if(self.fields is None):
            self._chkTable()
            
        return
    
    def _chkTable(self):
        if(self.ctrlType in CtrlTypes):
            ctype=CtrlTypes[self.ctrlType]
            
            self.fields=ctype["FLDS"]
            self.chktable=ctype["CHK"] % self.tbn
            self.createtable=ctype["CREATE"] % self.tbn
            
            chkCreateTable(self.dbw,CHK=self.chktable,CREATE=self.createtable)
            return
        
        raise errs.RbErr("error ctrl type %s" % self.ctrlType)
        
    def _check(self,rightStep):
        if(self.step!=rightStep):
          oldstep=self.step
          self.reset() ### reset for error
          raise  errs.RbErr(self.tbn+" the right step is %s but now is %s" % (str(self.flow[rightStep]),str(self.flow[oldstep])))        
     
    def begin(self,dbw=None):
        self.check(dbw)
        self._check(1)
        self.fetchRcd1()
        self.createRcd2()
        try:
          return  self.createWhereSQL()
        finally:
            self.step=2
    
    def fetchRcd1(self):
        pass
    
    def createRcd2(self):
        pass
    
    def createWhereSQL(self):
        return None
    
    def createDelSQL(self,delwhere):
        return None
    
    def okDone(self,delwhere):
        self._check(2)
        self._updateRcds()
        self.oked()
        
        return self.createDelSQL(delwhere)
    
    def oked(self):
        self.step=3
    
    def _updateRcds(self):
        pass    
    
    def end(self):
        self._check(3)
        self._doend()
        self.step=4
        
    def ended(self):
        if(self.step<len(self.flow)-1):
            return False
        
        return True

    def _doend(self):
        pass
    
def CtrlTB4Base(* arg):
    return _CtrlTB4Base(* arg)

class _CtrlTB4Base(_CtrlTB):  #Base controller
    def __init__(self,dbw,tbname,dtfield):
        _CtrlTB.__init__(self, dbw, tbname, dtfield)
        self.ctrlType="BASE"
        return
        
    def _init(self):
        #self.fields=["ID","CTD","LTD","STATUS"]        
        _CtrlTB._init(self)
        
        self.rcd1=None
        self.rcd2=createEmptyCtrlRcd(self.fields)
        
        self.sqls={"GETRCD1":"select %s from %s  where STATUS=1 order by CTD DESC" % (rbruntime.StringUtils.pAstr(self.fields, ","),self.tbn),
                   "GETRCD2":"select %s from %s  where STATUS=0 order by CTD DESC" % (rbruntime.StringUtils.pAstr(self.fields, ","),self.tbn),
                     "SETRCDST":" update " + self.tbn +"  set STATUS=%s where ID='%s'",
                     "DELST2":"delete from %s where STATUS=2 " % self.tbn,
                     "INSRCD2":"insert into %s(LTD) values(?)" % self.tbn,
                     "WHERESUB":"  where %s>? and %s<=?  " % (self.dtfield,self.dtfield),
                     "WHERESUBORDER":"  order by %s " % self.dtfield
                     }
        
        return
        
    def fetchRcd1(self):
        self.rcd1=setCtrlRcd(self.fields,self.dbw.fetchRs("ONE",self.sqls["GETRCD1"]),self.rcd1) 
        if( self.rcd1 is None):
             self.rcd1=createEmptyCtrlRcd(self.fields)
             self.rcd1["CTD"]=datetime.datetime(2000,1,1)
             
        return 
    
    # after v0.8.0
    def getCTD(self):
        return self.rcd1["CTD"]
    
    # after v0.8.0       
    def createRcd2(self):
        self.dbw.exe(self.sqls["INSRCD2"],self.getCTD())
        self.dbw.commit()
        self.rcd2=setCtrlRcd(self.fields,self.dbw.fetchRs("ONE",self.sqls["GETRCD2"]),self.rcd2) 
        #self.rcd2=self.dbw.fetchRs("ONE",self.sqls["GETRCD2"]) 
        
        if(self.rcd2 is None):
          raise  "error for new ctrl record"
      
        return         
    
    def createWhereSQL(self):
       return self.sqls["WHERESUB"]+self.sqls["WHERESUBORDER"],self.rcd2["LTD"]-deltasec,self.rcd2["CTD"]
    
    def createDelSQL(self,delwhere):
       if(delwhere is None):
          return None,self.rcd2["LTD"],self.rcd2["CTD"]
      
       return self.sqls["WHERESUB"]+delwhere,self.rcd2["LTD"]-deltasec,self.rcd2["CTD"]
   
    def _updateRcds(self):
        self.dbw.exe(self.sqls["SETRCDST"] % ("1",self.rcd2["ID"]))        
        if(self.rcd1["ID"] is not None):       
            self.dbw.exe(self.sqls["SETRCDST"] % ("2",self.rcd1["ID"]))    
            
        self.dbw.commit()
        
        return
    
    def _doend(self):
        self.dbw.exe(self.sqls["DELST2"]) 
        self.dbw.commit()
            
        return 

def CtrlTB4BaseD(* arg):
    return _CtrlTB4BaseD(* arg)
    
class _CtrlTB4BaseD(_CtrlTB4Base):  #Kaoqin controller
        def __init__(self,dbw,tbname,dtfield):
            _CtrlTB4Base.__init__(self, dbw, tbname, dtfield)
            return
       
        def _doend(self):
            self.dbw.exe(self.sqls["DELST2"]) 
            self.dbw.commit()
            
            return 
        
        # after v0.8.2
        def getCTD(self):
           if(self._inToryishe == True):#_setTbn
               return datetime.datetime(2000,2,2)  
           
           return _CtrlTB4Base.getCTD(self)   
             
 
class _CtrlTB4RealB(_CtrlTB):  #Base controller for real and patch real
    def __init__(self,dbw,tbname,dtfield):
        _CtrlTB.__init__(self, dbw, tbname, dtfield)    
        self.ctrlType="REAL"
        return 
    
    def _init(self):
        #self.fields=["ID","CTD","LTD","DTD","STATUS"]
        _CtrlTB._init(self)
        
        self.rcd1=None
        self.rcd2=createEmptyCtrlRcd(self.fields)
        self.rcd3=None
        
        tblselect=rbconf.getTbnWithLock(self.tbn, "select")
        tblupdate=rbconf.getTbnWithLock(self.tbn, "update")
        self.sqls={"GETRCD1":"select %s from %s  where STATUS=1 order by CTD DESC" % (rbruntime.StringUtils.pAstr(self.fields, ","),tblselect),
                   "GETRCD2":"select %s from %s  where STATUS=0 order by CTD DESC" % (rbruntime.StringUtils.pAstr(self.fields, ","),tblselect),
                   "GETRCD3":"select %s from %s  where STATUS=3 order by DTD " % (rbruntime.StringUtils.pAstr(self.fields, ","),tblselect),
                     "SETRCDST":" update " + tblupdate +"  set  STATUS=%s where ID='%s'",
                     "DELST2":"delete from %s where STATUS=2 " % self.tbn,
                     "INSRCD2":"insert into %s(LTD,DTD) values(?,?)" % self.tbn,
                     "INSRCD3":"insert into %s(CTD,LTD,DTD,STATUS) values(?,?,?,?)" % self.tbn,
                     "RCD2DDT":"",
                     "WHERESUB":"  where %s>? and %s<=?  " % (self.dtfield,self.dtfield),
                     "WHERESUBORDER":"  order by %s " % self.dtfield
                     }
        
        return
    
    def _updateRcd2(self):    
        pass
    
    def _updateRcd3(self,st):
        pass
    
    def _updateRcds(self):
        self._updateRcd2()
        self._updateRcd3(2)
        return

def CtrlTB4RealP(* arg):
    return _CtrlTB4RealP(* arg)
               
class _CtrlTB4RealP(_CtrlTB4RealB):  #controller for patch real
    def __init__(self,dbw,tbname,dtfield):
        _CtrlTB4RealB.__init__(self, dbw, tbname, dtfield) 
        
        return   
    
    def fetchRcd1(self):
        self.fetchRcd3()
             
        return      
        
    def fetchRcd3(self):
        #print self.tbn+".dbw:"+str(self.dbw)
        self.rcd3=setCtrlRcd(self.fields,self.dbw.fetchRs("ONE",self.sqls["GETRCD3"]),self.rcd3) 
        #self.rcd3=self.dbw.fetchRs(model="ONE",* self.sqls["GETRCD3"]) 
        #print self.tbn+".rcd3:"+str(self.rcd3)
        return 
    
    def createWhereSQL(self):
        def retTD(refP):
            refTD=datetime.datetime(2000,2,2) 
            try:
               if(refP._inToryishe == True):
                   return  (refTD,refP.rcd3["DTD"])
                
               return (refP.rcd3["LTD"],refP.rcd3["DTD"])
            except: 
                return (refTD,refTD)
        
        if(self.rcd3 is  None):
            return None,None,None #None,self.rcd3["LTD"],self.rcd3["DTD"]
        
        self._updateRcd3(5)
        retTDs=retTD(self)
        return self.sqls["WHERESUB"]+self.sqls["WHERESUBORDER"],retTDs[0],retTDs[1]
        #return self.sqls["WHERESUB"]+self.sqls["WHERESUBORDER"],self.rcd3["LTD"],self.rcd3["DTD"]
    
    def createDelSQL(self,delwhere):
        def retTD(refP):
            refTD=datetime.datetime(2000,2,2) 
            try:
               if(refP._inToryishe == True):
                   return  (refTD,refP.rcd3["DTD"])
                
               return (refP.rcd3["LTD"],refP.rcd3["DTD"])
            except: 
                return (refTD,refTD)
            
        if(self.rcd3 is  None  or delwhere is None):
            return None,None,None  #None,self.rcd3["LTD"],self.rcd3["DTD"]
        
        retTDs=retTD(self)
        return self.sqls["WHERESUB"]+delwhere,retTDs[0],retTDs[1]
        #return self.sqls["WHERESUB"]+delwhere,self.rcd3["LTD"],self.rcd3["DTD"]
    
    def _updateRcd3(self,st):
        if(self.rcd3 is  None):
            return
        
        self.dbw.exe(self.sqls["SETRCDST"] % (st,self.rcd3["ID"])) 
            
        self.dbw.commit()
        
        return
    
    def _doend(self):
        self.dbw.exe(self.sqls["DELST2"]) 
        self.dbw.commit()
        
        return   

def CtrlTB4Real(* arg):
    return _CtrlTB4Real(* arg)
    
class _CtrlTB4Real(_CtrlTB4RealB):  #controller for real 
    def __init__(self,dbw,tbname,dtfield):
        _CtrlTB4RealB.__init__(self, dbw, tbname, dtfield) 
        
        return   
    
    def _init(self):
         _CtrlTB4RealB._init(self)
         
         self.sqls["RCD2DDT"]="DATEADD(Ss,-%s,GETDATE())" % (rbCfg.IMPLEMENTS["REAL"]["TIMER"]*2)
         self.sqls["INSRCD2_"]="insert into %s(LTD,DTD) values(?,%s)" % (self.tbn,self.sqls["RCD2DDT"])
    
    def fetchRcd1(self):
        self.rcd1=setCtrlRcd(self.fields,self.dbw.fetchRs("ONE",self.sqls["GETRCD1"]),self.rcd1) 
        #self.rcd1=self.dbw.fetchRs(model="ONE",* self.sqls["GETRCD1"]) 
        if( self.rcd1 is None):
             self.rcd1=createEmptyCtrlRcd(self.fields)
             self.rcd1["CTD"]=datetime.datetime(2000,1,1)
             
        return 
    
    def ddtRcd2(self):#todo patch SQL create RCD2.DDT
        self.needP=False
        
        return 
    
    def setneedP(self):#todo  need patch
        self.needP= self.rcd2["LTD"]<self.rcd2["DTD"]          
        
        return
           
    def createRcd2(self):
        self.ddtRcd2()
        self.dbw.exe(self.sqls["INSRCD2_"],(self.rcd1["CTD"]))
        self.dbw.commit()
        self.rcd2=setCtrlRcd(self.fields,self.dbw.fetchRs("ONE",self.sqls["GETRCD2"]),self.rcd2) 
        #self.rcd2=self.dbw.fetchRs(model="ONE",* self.sqls["GETRCD2"]) 
        
        if(self.rcd2 is None):
          raise  "error for new ctrl record"
      
        self.setneedP()
      
        return 
    
    def _updateRcd2(self):    
        self.dbw.exe(self.sqls["SETRCDST"] % ("1",self.rcd2["ID"]))  
              
        if(self.rcd1["ID"] is not None):       
            self.dbw.exe(self.sqls["SETRCDST"] % ("2",self.rcd1["ID"]))
            
        if(self.needP):    
            self.dbw.exe(self.sqls["INSRCD3"],(self.rcd2["CTD"],self.rcd2["LTD"],self.rcd2["DTD"],3)) #self.rcd3["DTD"]
            
        self.dbw.commit()
        
        return      
    
    def createWhereSQL(self):
       ret=self.rcd2["DTD"]
       if(self.needP==False):
           ret=self.rcd2["LTD"]
           if(self._inToryishe == True):ret=ret-deltasec10
           
       return self.sqls["WHERESUB"]+self.sqls["WHERESUBORDER"]+" DESC",ret,self.rcd2["CTD"]
    
    # after 0.8.2
    def createDelSQL(self,delwhere):
        if(delwhere is None):
            return None,self.rcd2["LTD"],self.rcd2["DTD"]
        
        ret=self.rcd2["DTD"]
        if(self.needP==False):
           ret=self.rcd2["LTD"]
        
        ret1=self.rcd2["CTD"]   
        if(self._inToryishe == True):
            if(self.needP==False):ret=ret-deltasec10
            ret1=ret1-deltasec10  # or 
            pass
        
        return self.sqls["WHERESUB"]+delwhere,ret,ret1
        #return self.sqls["WHERESUB"]+delwhere,ret,self.rcd2["CTD"]

# up 0.8.2    
def inToryishes(titem):
   import Pojos
   return Pojos.inToryishes(titem)