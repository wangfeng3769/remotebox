__version__ = "1.0.0"
__version_os__ = ["linux","ubuntu","dtu"]
__version_date__ = "20120413"

'''
["win","SQL"]
["win","SQL","modem"]
["win","SQL","2008","modem"]
["win","SQL","2008","modify"]
["win","SQL","dtu"]
["win","SQL","2008","dtu"]
["linux","ubuntu","modem"]
["linux","ubuntu"]
["linux","ubuntu","modify"]
["linux","redhat"]
["linux","slax","hdc1"]
["linux","slax","hdc1","modify"]
["linux","slax","sda1"]
["linux","slax","sda1","modify"]
'''

_DBLocks={} # {"select":"","update":""}
_osDone=""

_commdirs=[]
_freetdscfg=[]

_workTypes={}
_CMDFILTER={}

_Deamons={}

delay={'recv':1,'recv_time':1,'file10':1} # reduce cpu usage and syn socket

TRAN_EX={'DataFrom':{"win":"0","linux":"1"}
         ,'LocalReboot':{"slax"}
         ,"SQLDrv":{"2000":'{SQL Server}',"2005":'{SQL Server}','2008':'{SQL Server Native Client 10.0}'}}

# edit up v0.8.1
def onOs():
    def modifydb():
        _DBLocks["select"]="  with(NOLOCK) "
        _DBLocks["update"]="  with(ROWLOCK HOLDLOCK) "
        
        return
    
    def onModify():
        pos=["modify","modify1"]
        for op in pos:
            if(op in __version_os__):
               eval(op)()
               
        modifydb()
        
    def slax(): 
        if(len(__version_os__)>2)    :   
            _commdirs.append("/mnt/%s/slax/rootcopy/data/zhongan/" % __version_os__[2])
            _freetdscfg.append("/mnt/%s/tds/etc/freetds.conf" % __version_os__[2])
            
        onModify()
            
        return
    
    def simpleLocalPageItem():
        import conff
        #conff.TRAN[]
        conff.CONFIGPAGES['LOCAL']=["LOCAL_CAPTYPE"]
        return
    
    def ubuntu():
        _freetdscfg.append("/etc/freetds/freetds.conf")  
        _freetdscfg.append("/usr/local/freetds/etc/freetds.conf") 
         # "/usr/local/freetds/etc/freetds.conf"  "/etc/freetds/freetds.conf"
        
        onModify()
            
        return
    
    def modify():
        _workTypes.clear()
        
        #_workTypes["BASE"]=["BASE","ATTEN"]
        #_workTypes["REAL"]=["REAL","REAL1"]
        _workTypes["REAL"]=["BASE","ATTEN","REAL","REAL1"]
        _workTypes["REALP"]=["REAL","REAL1"]
        _CMDFILTER['3']=['ZAYHRL','ZAYHPTH']
        
        '''
        _workTypes["BASE"]=["BASE"]
        _workTypes["REAL"]=["ATTEN","REAL","REAL1"]
        _workTypes["REALP"]=["REAL","REAL1"]
        _CMDFILTER['3']=['ZAYHRL','ZAYHPTH','ZAYHBSE','ZAYHRPT']  
        '''
                
        _Deamons["Reduce"]="onMult"
        _Deamons["Monitor"]=False
        
        #modem()
        
        return
    
    def modify1():
        _workTypes.clear()
        
        _workTypes["BASE"]=["BASE","ATTEN"]
        _workTypes["REAL"]=["REAL","REAL1"]
        #_workTypes["REAL"]=["BASE","ATTEN","REAL","REAL1"]
        _workTypes["REALP"]=["REAL","REAL1"]
        #_CMDFILTER['3']=['ZAYHRL','ZAYHPTH','ZAYHRPT']
        _CMDFILTER['3']=['ZAYHRL','ZAYHPTH','ZAYHBSE']
        
        '''
        _workTypes["BASE"]=["BASE"]
        _workTypes["REAL"]=["ATTEN","REAL","REAL1"]
        _workTypes["REALP"]=["REAL","REAL1"]
        _CMDFILTER['3']=['ZAYHRL','ZAYHPTH','ZAYHBSE','ZAYHRPT']  
        '''
                
        #_Deamons["Reduce"]="onMult"
        _Deamons["Monitor"]=False
        
        #modem()
        
        return
    
    def modem():
        import rbcommit.cmodem as cmodem
        cmodem.setModem(1)
        
        return
    # after 0.8.5
    def dtu():
        import rbcommit.cmodem as cmodem
        TRAN_EX["transmit"]="dtutrans"
        cmodem.setModem(2)
        modify()
        return 
        
    
    def win():
        if("modify" in __version_os__):
            modify()
            
        import rbruntime.cmdexe as cmdexe
        cmdexe.reworksh["rework"]=""
        cmdexe.reworksh["upgrework"]=""
        
        return 
    
    def linux(): # 1.0.0
        import rbruntime.cmdexe as cmdexe,os
        cmdexe.reworksh["rework"]="bash %s/startWorker.sh" % os.getcwd()
        cmdexe.reworksh["upgrework"]="bash %s/startUpgWorker.sh" % os.getcwd()
        
        return
    
    global _osDone,_commdirs,_freetdscfg,_DBLocks
    if(_osDone==""):
        pos=["linux","slax","ubuntu","modem","dtu","win"]
        for op in pos:
            if(op in __version_os__):
               #print op
               eval(op)()
               
        _osDone=__version__
        
    return

def getTbnWithLock(tbn,sqln="select"):
    if(type(tbn)==type('') and sqln in _DBLocks):
        return tbn+_DBLocks[sqln]
    
    return tbn

def getWinSQLDriver():
    ret='{SQL Server}'
    if("SQL" in __version_os__ and len(__version_os__)>2 and __version_os__[2] in TRAN_EX["SQLDrv"]):
        ret=TRAN_EX["SQLDrv"][__version_os__[2]]
        
    return ret

def setWinService():
    _Deamons["winservice"]="Y"
    
    return

def hasWinService():    
    return "winservice" in _Deamons

def testLocalReboot():
    for v in __version_os__:
       if v is None: continue
       if v.lower() in  TRAN_EX["LocalReboot"]: return "Y"
       
    return "N"

def testSock(srcF):
    ret=srcF
    
    if("transmit" in TRAN_EX and type(TRAN_EX["transmit"])==type("pytrans") and type(TRAN_EX["transmit"])==type(srcF)):
        if(srcF <> "pytrans"):
	       ret=TRAN_EX["transmit"]

    return ret

#onOs()