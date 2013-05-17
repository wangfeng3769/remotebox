'''
Created on 2011-8-3

@author: Tanglh
'''

import shutil,ConfigParser,time
import dirfile,cmdexe
import rbconf
import rbconf.conff as conff
import rblog.worklog as wlog

shutdowncmd="shutdown"
rebootcmd="shutdown -r 0"

commdirs=[] #["/mnt/sda1/slax/rootcopy/data/zhongan/","/mnt/hdc1/slax/rootcopy/data/zhongan/"]

freetdscfg=None
#"/usr/local/freetds/etc/freetds.conf" #ubantu
#freetdscfg="/mnt/hdc1/tds/etc/freetds.conf" #slax
freetdssec="KJ133"

unixODBC_DSN="FreeTDS"  #"Freetds"

#linuxDBStr={"SERVERNAME":freetdssec}
linuxDBStr={"DRIVER":'{%s}' % unixODBC_DSN,"SERVERNAME":freetdssec}

def copyLocalIP(src):
    dirfile.copyFileToDirs(src,* commdirs)
    return 

def doShutdown():
    ret=cmdexe.runcmd(shutdowncmd)
    return

def doReboot():
    ret=cmdexe.runcmd(rebootcmd)
    return

def inLinux():
    os=rbconf.__version_os__
    '''
    re=[os,os[0],type(os[0]) is type(''),os[0].lower()=="linux"]
    print re
    wlog.getLogger().debug(str(re))
    '''
    return os[0]  and type(os[0]) is type('')  and os[0].lower()=="linux"

def doBuildDSCfgByDB(fdb):
        yes=fdb["LOCAL_CAPTYPE"]
        if(yes<>"DB"):
            return
        
        cf=ConfigParser.RawConfigParser()
        #cfile=open(freetdscfg,'r+')
        cf.read(freetdscfg)
        secs= cf.sections()
        '''
        for se in secs:
            print se
        '''
        #cfile.close()
         
        if not cf.has_section(freetdssec):
            cf.add_section(freetdssec)
        
        cf.set(freetdssec, 'host', fdb["DB_IP"])
        cf.set(freetdssec, 'port', fdb["DB_PORT"])
        
        
        cfile=open(freetdscfg,'wb')
        cf.write(cfile)
        cfile.close()
        
        return
    
def setDataFrom4OS():
    if('DataFrom' not in rbconf.TRAN_EX):
        return
    
    os=rbconf.__version_os__
    if(os[0] and os[0] in rbconf.TRAN_EX['DataFrom']):
        conff.TRAN['DataFrom']=rbconf.TRAN_EX['DataFrom'][os[0]]
        #doPrint( "setDataFrom4OS",conff.TRAN['DataFrom'])
        
    return

def doPrint(* arg):
    if(rbconf.hasWinService()):
        return
    
    try:
        print arg
    except: 
        wlog.getLogger().error("Linux doPrint ignor:")
        wlog.doTraceBack()
        
    return

def beforeRemoteStart():# 1.0.0.1
    if("server" in conff.WEB):
        try:
            conff.WEB["server"].shutdown()
            wlog.getLogger().debug('conff.WEB.server shutdowned')
        except :
          wlog.doTraceBack()  
          
    time.sleep(2)
    
    return

def remoteBoxRework():
    beforeRemoteStart()
    cmd=cmdexe.reworksh["rework"]
    doReworkBySh(cmd)
    return

def remoteBoxUpgRework():
    beforeRemoteStart()
    cmd=cmdexe.reworksh["upgrework"]
    doReworkBySh(cmd)
    return

def doReworkBySh(cmd):
    def dowin():
        return
    
    def dolinux():
        return cmdexe.runcmd(cmd)
    
    if(inLinux()):
        return dolinux()
    
    return dowin()
    
if(freetdscfg is None):
    rbconf.onOs()
    setDataFrom4OS()
    conff.TRAN['transmit']=rbconf.testSock(conff.TRAN['transmit'])
    conff.TRAN['LocalReboot']=rbconf.testLocalReboot()
    if(len(rbconf._freetdscfg)>0):
        freetdscfg=rbconf._freetdscfg[0]
    commdirs=rbconf._commdirs
    #print freetdscfg,commdirs