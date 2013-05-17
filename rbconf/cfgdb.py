'''
Created on 2011-8-2

@author: Tanglh
'''

import os,sys,anydbm,ConfigParser
import rbruntime.dirfile as dfile
import rblog.worklog as wlog
import rbconf
import conff

dbf="cfgapp.cfg"
dbuser="cfgapp.user"

STATUSKEY="STATUS"
STATUS1stV="0"
DEVCODEKEY="DEVCODE"
DEVCODE1stV="00000000000"

LOCAL_IP_K="LOCAL_IP"
LOCAL_IP_V="192.168.0.2"
LOCAL_MASK_K="LOCAL_MASK"
LOCAL_MASK_V="255.255.255.0"
LOCAL_GATE_K="LOCAL_GATE"
LOCAL_GATE_V=""
LOCAL_CAPTYPE_K="LOCAL_CAPTYPE"
LOCAL_CAPTYPE_V="NONE"

UPDATEAUTOKEY="UPDATE_AUTO"
UPDATE_AUTO_Y="Y"
UPDATE_AUTO_N="N"

INITCFG={STATUSKEY:STATUS1stV,DEVCODEKEY:DEVCODE1stV,LOCAL_IP_K:LOCAL_IP_V,LOCAL_MASK_K:LOCAL_MASK_V,
         LOCAL_GATE_K:LOCAL_GATE_V,LOCAL_CAPTYPE_K:LOCAL_CAPTYPE_V,UPDATEAUTOKEY:UPDATE_AUTO_N}

SA="sa"
SAPSW="sa123456"
MONITOR="monitor"
INITUSER={SA:SAPSW}

refpath=None

isfirst=True

def cfgdb():
    return _cfgdb(getCfgDBF())

def userdb():
    return _cfgdb(getUserDBF())

def _cfgdb(pdb):
    return anydbm.open(pdb, 'c')

def getCfgDBF():
    return dfile.joinPath(chkcfgPath(conff.cfgpath), dbf)

def getCommCfg():
    return dfile.joinPath(chkcfgPath(conff.cfgpath), conff.commcfg)

def getUserDBF():
    return dfile.joinPath(chkcfgPath(conff.cfgpath), dbuser)

def chkcfgPath(cfgpath):
    path=""
    if(cfgpath is not None):
        path=cfgpath
        
    if(path==""):return path
    
    dfile.chkCreateDir(path)
    
    return path

def initCfg(fdb):
    fdb.clear()
    updateCfgm(fdb,**INITCFG)
    
    return
    
def initUser(udb):
    udb.clear()
    updateCfgm(udb,**INITUSER)
    
    return

#after 0.8.7
def initVolCfg():
    import cfgvol
    cfgvol.initCfgVol()
    
    return

def updateCfgm(fdb,** kvs):
    fdb.update(** kvs)
    
    return

def updateCfg(** kvs):
    fdb=cfgdb()
    try:
        updateCfgm(fdb,** kvs)
        return "S_OK"
    except:
        return "F_UPDATECFG"
    finally:
        fdb.close()

def getCfgmValues(fdb,* ks):
    ret={}
    for k in ks:
        if k in fdb :
            ret[k]=fdb[k]
            
    return ret

def getCfgedValues(* ks):
    fdb=cfgdb()
    try:
        return getCfgmValues(fdb,* ks)
    finally:
        fdb.close()

def onCfg(init=False):
    fdb=cfgdb()
    udb=userdb()
    if(fdb is None or udb is None):
        return
    
    # import shutil
    # shutil.copy(getCfgDBF(), 'C:/')
    
    if(init or STATUSKEY not in fdb or fdb[STATUSKEY]==STATUS1stV):
        initCfg(fdb)
        initUser(udb)
        initVolCfg()
        
    freshConfByDB(fdb)
    freashCfgVol()
        
    fdb.close()
    udb.close()
    
def userDBAuth(user,psw):
    if(user is None):
        return "F_NoneUser"
    
    udb=userdb()
    if(udb is None):
        return "F_NoUser"
    
    try:
        if(user not in udb):
            return "F_NoUser"
        
        v=udb[user]
        if(psw==v):
            return "S_OK"
        
        return "F_ErrPSW"
    finally:
        udb.close()
        
def filterByCfgKey(key):
    if(key is None):
        return None
    
    fdb=cfgdb()
    if(key not in fdb):
        return None
    
    try:
        return fdb[key]
    finally:
       fdb.close() 
       
def getSTATUS(fdb):
    sts=0
    try:sts=int(fdb[STATUSKEY])
    except:wlog.doTraceBack()
    
    return sts

def getCfgSTATUS():
    fdb=cfgdb()
    
    sts=fdb[STATUSKEY]
    ists=getSTATUS(fdb)
    fdb.close()
    
    return sts,ists

def configCMDs(user=None):
    ret=[]
    ret.extend(conff.CMDCONS)
    fdb=cfgdb()
    
    sts=fdb[STATUSKEY]
    ists=getSTATUS(fdb)
    fdb.close()
    
    import rbruntime.StringUtils as rsutils
    if(sts == '0'):
            ret.extend(rsutils.joinListHaveFilter(conff.CMDFILTER['0']))
            return ret
        
    if(conff.RUNMSG["COMM"] is "OK"): 
        return ret
        
    if(user=='sa'):
            ret.extend(rsutils.joinListHaveFilter(conff.CMDFILTER['0']))
            
    ret.extend(rsutils.joinListHaveFilter(conff.CMDFILTER['1']))
    
    
    for i in range(2,ists+1):
        ssi=str(i)
        if(ssi in conff.CMDFILTER):ret.extend(rsutils.joinListHaveFilter(conff.CMDFILTER[ssi]))
    
    '''    
    if(sts == '2'):
            ret.extend(rsutils.joinListHaveFilter(conff.CMDFILTER['2']))
            
    if(sts == '3'):
            ret.extend(rsutils.joinListHaveFilter(conff.CMDFILTER['2']))
            ret.extend(rsutils.joinListHaveFilter(conff.CMDFILTER['3']))
    '''     
    return ret    

def  chkDevCode(value): 
    if(type(value) is type('') and len(value)==11):
        if(value==DEVCODE1stV):
            return "Err_1st"
        return "S_OK"  
    
    return "Err_TypeLen"
    
def cfgDevCode(value):  
    msg=chkDevCode(value)  
    if(msg != "S_OK"):
        return msg
    
    fdb=cfgdb()
    fdb[DEVCODEKEY]=value #STATUSKEY
    fdb[STATUSKEY]="1"
    fdb.close()
    
    return msg

def freshConfByDB(fdb=None):
    if(fdb is None):fdb=cfgdb()
    
    freshTRANByDB(fdb)
    
    freshDBStrByDB(fdb)
    freshFtpCfgByDB(fdb)
    
    freshIMPLEMENTSByDB(fdb)
    freshIMPLEMENTADDSByDB(fdb)
    
    fdb.close()
    
    return

#after 0.8.7
def devCodeTail5():
    dcode=conff.TRAN["DeviceCode"]
    if(dcode==DEVCODE1stV):
        return 0
    
    return dcode[-5:]

#after 0.8.7
def freashCfgVol():
    import cfgvol
    cfgvol.setUPGState(0)
    cfgvol.freashCfgVol()

def freshTRANByDB(fdb):
    conff.TRAN["Locator"]=""
    conff.TRAN["DeviceCode"]=fdb["DEVCODE"]
    conff.TRAN["CAP"]=None
    
    # after 0.8.7 "CTRLNO"
    if(conff.TRAN["CTRLNO"] is None or str(conff.TRAN["CTRLNO"])=='0'):
        conff.TRAN["CTRLNO"]=devCodeTail5()
    # after 1.0.0 "CTRLNO"    
    wlog.getLogger().debug("CTRLNO:"+str(conff.TRAN["CTRLNO"]))    
    return

def freshDBStrByDB(fdb):    
    def commDBStr():
        return {"DATABASE":'intranet',
                "PAGESIZE":500}
    
    def winDB(fdb):# {SQL Server Native Client 10.0}  {SQL Server}
        return {"DRIVER":rbconf.getWinSQLDriver(),"SERVER":fdb["DB_IP"],"PORT":fdb["DB_PORT"]
                ,"PAGESIZE":50}
    
    def linuxDB(fdb):
        import rbruntime.Linux as linux
        return linux.linuxDBStr
    
    def dbUserPSW(fdb):
        return {"UID":fdb["DB_USER"],"PWD":fdb["DB_PSW"]}
    
    def dbDriverServer(fdb):
        if(inLinux()):return linuxDB(fdb)
        
        return winDB(fdb)
    
    if("DB_USER" not in fdb):return
    if(conff.db is None):conff.db=commDBStr()
    if(fdb["LOCAL_CAPTYPE"]=="DB"):
        conff.db.update(dbUserPSW(fdb))
        conff.db.update(dbDriverServer(fdb))
        wlog.getLogger().debug(str(conff.db))
        
        freshCAPTYPE(fdb)
    
    return   

def freshFtpCfgByDB(fdb):    #["FTP_IP","FTP_PORT","FTP_USER","FTP_PSW"]
    for v in conff.ftp:
        conff.ftp[v]=None
    
    if("FTP_USER" not in fdb):return    
    if(fdb["LOCAL_CAPTYPE"]=="FTP"):
        for v in conff.ftp:            
          conff.ftp[v]=fdb["FTP_"+v]        
        freshCAPTYPE(fdb)
        
    return

def freshCAPTYPE(fdb):  
    conff.TRAN["CAP"]=fdb["LOCAL_CAPTYPE"] 
    
    conff.freshCfgLsnrPages()
    return

def passByEnable(fdb,pri,nbl=(None,"Y")):
    if(type(nbl) is not type(()) and len(nbl)!=2): return True
    if(nbl[0] is None or nbl[1] is None ):return True
    
    sts=getSTATUS(fdb)
    if sts <conff.STSBARRIER["DISBL"] :return False
    
    row=pri+nbl[0]
    if(row in fdb ):return fdb[row]==nbl[1]
    
    return False  

def enableADeamonRunByDB(fdb,pri="",nbl=("","Y")):  
    fdb[pri+nbl[0]]=nbl[1]
    return

def enableDeamonsRunByDB(fdb,rms={},nbl=("","Y")):
    for imm in rms:
        pri=rms[imm]["CFGPRI"]
        enableADeamonRunByDB(fdb,pri,nbl)
        
    return

def disableDeamonRun(): 
    fdb=cfgdb()
    nbl=("EBL","N")
    try:
        enableDeamonsRunByDB(fdb,conff.IMPLEMENTS,nbl)
        enableDeamonsRunByDB(fdb,conff.IMPLEMENTADDS,nbl)
        #return "S_OK"
    except:
        pass
    finally:
        fdb.close()
        
def returnRemote(fdb,pri="",nbl=(None,"Y"),retn=2):
    def toint(strr,defaultv):
        ret=defaultv
        try:
          ret=int(strr)  
        except:
          ret=defaultv
      
        return ret
    
    ret=[None,60]
    if(retn==3):
      ret[2]=None
    
    if(passByEnable(fdb,pri,nbl)):
        ret[0]=(fdb[pri+"IP"],toint(fdb[pri+"PORT"],-1))
        ret[1]=toint(fdb[pri+"TIMER"],60)
        
        ftpp=pri+"FTPPATH"
        if(retn==3 and ftpp in fdb):
            ret[2]=fdb[ftpp]
        return ret
        
    return ret   

def freshRemoteSByDB(fdb,rms={},retn=2):    
    for imm in rms:
        pri=rms[imm]["CFGPRI"]
        nbl=("EBL","Y")  #nbl=(pri+"EBL","Y")
        ret=returnRemote(fdb,pri,nbl,retn)
        rms[imm]["REMOTE"]=ret[0]
        rms[imm]["TIMER"]=ret[1]
        rms[imm]["FTPPATH"]=None
        if(retn==3):rms[imm]["FTPPATH"]=ret[2]
        freshRunCmdByRemote(imm,rms[imm]["REMOTE"])
        
    return 

def freshIMPLEMENTSByDB(fdb):
    retn=2
    if(conff.TRAN["CAP"]=="FTP"):
       retn=3
    
    #print "freshIMPLEMENTSByDB",rbconf._workTypes
    conff.freshImpTypes(** rbconf._workTypes) 
    conff.freshRunCmd()  
    freshRemoteSByDB(fdb,conff.IMPLEMENTS,retn)   
    conff.freshCMDFILTER(** rbconf._CMDFILTER)
    freshRealPByDB(fdb)
         
    return 
    
def freshIMPLEMENTADDSByDB(fdb):
    freshRemoteSByDB(fdb,conff.IMPLEMENTADDS)  
    return 

def freshRealPByDB(fdb):
    import rbdatabase.Pojos as pjs
    
    key=[]
    try:    
        if("REALP" not in conff.IMPLEMENTS or conff.IMPLEMENTS["REALP"]["REMOTE"] is None):
            return
        
        if(conff.TRAN["CAP"]<>"DB"):
            return
        
        for k in set(["REAL1","REAL"]) & set(conff.IMPLEMENTS.keys()):
            if(conff.IMPLEMENTS[k]["REMOTE"] is not None):
                key.append(k)
        #print "freshRealPByDB",rbconf._workTypes   ,key 
        
        return
    finally:
        pjs.freshRealP(* key)
        pjs.freshWorkPojos(** rbconf._workTypes)

def freshRunCmdByRemote(key,rmt):
    import cfgcmd
    if(key in conff.RUNMSG and key is not "COMM"):
        if(rmt is None):cfgcmd.setCmd(**{key:"DISENLE"})
        else:cfgcmd.setCmd(**{key:conff.RUNMSG["COMM"]})

def inLinux():
    import rbruntime.Linux as linux
    return linux.inLinux()

def updateCfgByDBInLinux(* func):
    if(inLinux()):
        fdb=cfgdb()
        for f in func:
           f(fdb)
        fdb.close()
        
    return

def updateLocalCfgByDB():
    def doBuildLocalCfgByDB(fdb):#getCommCfg
        cf=ConfigParser.RawConfigParser()
        
        cf.add_section("LOCAL")
        cf.set("LOCAL", 'ip', fdb["LOCAL_IP"])
        cf.set("LOCAL","netmask",fdb["LOCAL_MASK"])
        cf.set("LOCAL","route",fdb["LOCAL_GATE"])
        
        cfile=open(getCommCfg(),'wb')
        cf.write(cfile)
        cfile.close()
        
        return
    
    def doCopyLocalCfg(fdb):
        import rbruntime.Linux as linux
        linux.copyLocalIP(getCommCfg())
        
        return
    
    updateCfgByDBInLinux(doBuildLocalCfgByDB,doCopyLocalCfg)
    return

def updateDataSourceByDB():
    def doBuildDSCfgByDB(fdb):
        import rbruntime.Linux as linux
        linux.doBuildDSCfgByDB(fdb)
        
        return
    
    def doCopyDSCfg(fdb):
        pass
    
    updateCfgByDBInLinux(doBuildDSCfgByDB)
    return

def setRunWhenStart(* funs):
    fdb=cfgdb()
    conff.RUNMSG["COMM"]="STOP"
    
    import cfgcmd
    sts=getSTATUS(fdb)
    if(sts>=conff.STSBARRIER["AUTORUN"]):
        conff.RUNMSG["COMM"]="OK"
    
    cfgcmd.notifyCommCmd()
    
    for f in funs:
        f(fdb)
        
    fdb.close()
    
    return