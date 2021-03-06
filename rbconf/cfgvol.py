'''
Created on 2012-3-26
after 0.8.6
@author: tanglh
'''

import cfgdb,datetime
import rbruntime.ParseString as ppstr
import rbruntime.StringUtils as StringUtils
import rbruntime.dirfile as dfile
import rblog.worklog as wlog
import rbconf
import conff,cfgdb
 
cfgvolu="vol.upg"  # vol upgraded

BCKPATH=""
RARPATH=""
TEMPEXPATH=""
RunVolKeys={}
UpgVolKeys={}

UPGSTATE=["STOP","DOING","DONE"]

upg={'headtag':"&&&&",'maxARead':1024*8,'maxFTimes':3,'restart':"startBox",'enable':'Y'
     ,'actions':['HAND','DOWN','SSOK','FAIL','STOP','DONE']
     ,'action':{'cur':None,'next':None,'times':0}
     ,'workpath':{'pdtar':'upg/downs/','pctar':'upg/cur/','pback':'upg/back/','ptestex':'upg/testex/','pworkex':'upg/workex/'}
     ,'logtag':"UPG",'worktime':{'begin':'03:00','format':ppstr.dtfomatter['Time2'],'maxLast':2,'state':UPGSTATE[0]}
     ,'worktimems':['00','10','20','30','40','50']
     ,'worktimehs':['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
     }
upgmsg={"request":{"msg":"","res":None}        
        ,'curRunVol':"",'curDown':{'vol':None,'size':-1},'downloads':[]}

def onWorkPath(bpath):
    #rbcfg.cfgpath=dfile.joinPath(rbcfg.basepath,rbcfg.cfgpath)
    def isSPath(pp):
        return type(pp)==type('') and pp.startswith('upg/')
    
    for pp in upg['workpath']:
        if(isSPath(upg['workpath'][pp])):
            upg['workpath'][pp]=dfile.joinPath(bpath,upg['workpath'][pp])
            dfile.chkCreateDir(upg['workpath'][pp])
    return

def getVolDBF():
    return dfile.joinPath(cfgdb.chkcfgPath(conff.cfgpath), cfgvolu)

def voldb():
    return cfgdb._cfgdb(getVolDBF())

def getCurVol():
    #return "0000000807"
    return getCVol()  #"ERR_RECV"
    
def getLastOKVol():
    oks=upgmsg['downloads']
    if(len(oks)<1):
        return None
    
    return oks[len(oks)-1]

def getCurDown():
    if(type(upgmsg['curDown']['vol'])==type('') and len(upgmsg['curDown']['vol'])==10):
        return upgmsg['curDown']['vol']
    
    return None
    
def getCVol():
    ret=getLastOKVol()
    if(ret is None):
        return upgmsg['curRunVol']
    
    return ret

def setCurVol(strv):
    pass

def setUpgradeVol(strv):
    pass

def isMaxVol(vol,refv):
    if(vol is None):
        return False
    
    if(refv is None):
        return True
    
    return int(vol)>int(refv)
    

def downs2Str():
    return StringUtils.strLst2String(upgmsg['downloads'], ',')

def downsStr2Lst(downstr):
    ret=[]
    if(type(downstr)==type('') and len(downstr)>0):
        ret=downstr.split(',')
        
    return ret

def filterDowns(downs):
    rvol=int(upgmsg['curRunVol'])
    ret=[]
    
    if(type(downs)==type(ret)) :
        for d in downs:
            if(isMaxVol(d,upgmsg['curRunVol'])):
                ret.append(d)
                
    return ret

def runVol():
    if(type(upgmsg['curRunVol']) is type('') and len(upgmsg['curRunVol'])==10):
        return upgmsg['curRunVol'] 
    
    upgmsg['curRunVol']=parseVolstr2Tenstr(rbconf.__version__)
    
    return upgmsg['curRunVol']    
        
def persistCfgVol():
    def toStr(v,dv="None"):
        if(v is None):
            return dv
        
        return str(v)
    
    vls={}
    vls['enable']=toStr(upg['enable'],'N')
    vls['curRunVol']=runVol()  #upgmsg['curRunVol'] 'maxLast'
    vls['downloads']=downs2Str()
    vls['worktime']=upg['worktime']['begin']
    vls['maxLast']=str(upg['worktime']['maxLast'])
    
    vdb=voldb()
    
    cfgdb.updateCfgm(vdb, ** vls)
    vdb.close()
    return

def initCfgVol():
    def doinit(vdb):
        runVol()
        upg['enable']='N'
        vdb.clear() 
        vdb.close()
        persistCfgVol()
        
        return
    
    def doclose(vdb):
        vdb.close()
        return
    
    vdb=voldb()
     
    if('downloads' in vdb):return doclose(vdb)    
    return doinit(vdb)
    
def freashCfgVol():
    def parseNone(v,dv='None'):
        if(v==dv):
            return None
        
        return v
    
    def getDowns(downstr):
        downs=downsStr2Lst(downstr)
        
        return filterDowns(downs)
        
    vls=voldb()
    if('enable' not in vls):
        vls.close()
        initCfgVol()
        return
    
    upg['enable']=vls['enable']
    upgmsg['curRunVol']=vls['curRunVol']
    upgmsg['downloads']=getDowns(vls['downloads'])
    upg['worktime']['begin']=vls['worktime']
    upg['worktime']['maxLast']=int(vls['maxLast'])
    vls.close()
    return

def parseTenstr2Volstr(tenstr):# 0000100806 --> 1.8.6
    vols=None
    if(type(tenstr)==type('') and len(tenstr)==10 and int(tenstr)):
        v1=int(tenstr[:5])
        v2=int(tenstr[5:8])
        v3=int(tenstr[8:])
        
        vols=str(v1)+"."+str(v2)+"."+str(v3)
        
    return vols

def parseVolstr2Tenstr(volstr):# 1.8.6 -->00100806
    vols=None
    if(type(volstr)==type('')):
       vs=volstr.split('.')
       if(len(vs)==3):
           v1=StringUtils.toFixStr(int(vs[0]), "00000")
           v2=StringUtils.toFixStr(int(vs[1]), "000")
           v3=StringUtils.toFixStr(int(vs[2]), "00")
           
           vols=str(v1)+str(v2)+str(v3)
    return vols

def getUpgVolDBF():
    return dfile.joinPath(cfgdb.chkcfgPath(conff.cfgpath), cfgvolu)

def isTime4Upg():
    def getNow():
        now1=datetime.datetime.now()
        
        return now1.strptime(now1.strftime(upg['worktime']['format']),upg['worktime']['format'])
    
    def inUpg():
        now1=getNow()
        t1=datetime.datetime.strptime(upg['worktime']['begin'],upg['worktime']['format'])
        delta = datetime.timedelta(hours=upg['worktime']['maxLast'])
        
        return t1<=now1<t1+delta
    
    return inUpg()
    #return True

def state4UPG():
    def stateIn():
        if(upg['worktime']['state']==UPGSTATE[0]):
            return True
        
        return False
    
    def stateOut():
        if(upg['worktime']['state']==UPGSTATE[2]):
            setUPGState(0) #upg['worktime']['state']=UPGSTATE[0]
            
        return False
    
    ok=isTime4Upg()
    if(ok==True):
        return (ok,stateIn(),upg['worktime']['state'])
    
    return (ok,stateOut(),upg['worktime']['state'])

def setUPGState(st):     
    def setIntState(st):  
        if(st>=0 and st<len(UPGSTATE)):
            upg['worktime']['state']=UPGSTATE[st]
            
        return
    
    def setStrState(st):
        if(st in UPGSTATE):
            upg['worktime']['state']=st
            
        return
    
    if(type(st)==type(0)):
        return setIntState(st)
    
    return setStrState(st)

def cfgvolToCtx(ctx):
    if(ctx is None):
        return
    
    btime=upg['worktime']['begin'].split(":")
    ctx['values']['UPDATE_AUTO']=upg['enable']
    ctx['values']['UPDATE_TIME_H']=btime[0]
    ctx['values']['UPDATE_TIME_M']=btime[1]
    
    ctx['SELECT']["UPDATE_TIME_H"]=upg['worktimehs']
    ctx['SELECT']["UPDATE_TIME_M"]=upg['worktimems']
    return ctx

def ctxToCfgvol(ctx):
    if(ctx is None):
        return ctx
    
    upg['enable']=ctx['values']['UPDATE_AUTO']
    upg['worktime']['begin']=ctx['values']['UPDATE_TIME_H']+":"+ctx['values']["UPDATE_TIME_M"]
    
    #ctx['SELECT']["UPDATE_TIME_H"]=upg['worktimehs']
    #ctx['SELECT']["UPDATE_TIME_M"]=upg['worktimems']
    
    persistCfgVol()
    
    return ctx