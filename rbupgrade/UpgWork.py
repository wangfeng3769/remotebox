'''
Created on 2012-4-11

@author: tanglh
'''

import UpgMode as umode
import rbconf,os
import rbconf.conff as rbcfg
import rbconf.cfgvol as cfgvol
import rbruntime.dirfile as dfile

def getRbBckModPath(basep,mod="RemoteBox"):
    return dfile.joinPath(basep, mod)

def backupCurVol():
    vol=cfgvol.upgmsg['curRunVol']
    src=rbcfg.apppath
    ptar=dfile.joinPath(cfgvol.upg['workpath']['pworkex'], vol)
    
    dfile.copyDirToDir(src, ptar, umode.bckdirmode, umode.bckfilemode)
    
    bcktar=dfile.joinPath(cfgvol.upg['workpath']['pback'], vol+umode.filefix["backup"])
    dfile.tarADir(bcktar, ptar, "RemoteBox") # dfile.tarADir(bcktar, ptar, vol)
    dfile.delete_file_folder(ptar)
    return

def curDown2History():
    src=cfgvol.upg['workpath']['pctar']
    ptar=cfgvol.upg['workpath']['pdtar']
    
    dfile.copyDirToDir(src, ptar, {}, {})
    #dfile.clsDir(src)
    return

def fullCurTarDirFile():
        base=cfgvol.upg['workpath']['pworkex']
        vol=cfgvol.getLastOKVol()
        if(vol is None):
            return [None,None]
        
        dir=dfile.joinPath(base, vol) 
        file=dir+umode.filefix["cdown"]
        return [dir,file] 

def integerCurDowns():
    def createTarFile():
        return fullCurTarDirFile()[1]
    
    def getCurs():
        ret=[]
        base=cfgvol.upg['workpath']['pctar']
        cfgvol.upgmsg['downloads'].sort()
        for r in cfgvol.upgmsg['downloads']:
           ret.append(dfile.joinPath(base, r+umode.filefix["down"])) 
           
        return ret
    
    def getExCurs():
        ret=[]
        base=cfgvol.upg['workpath']['ptestex']
        cfgvol.upgmsg['downloads'].sort()
        for r in cfgvol.upgmsg['downloads']:
           exdir=dfile.joinPath(base, r)
           if(os.path.exists(exdir)):
               ret.append(exdir) 
           
        return ret
    
    def dirToOne(curs,tard):
        for c in curs:
            dfile.copyDirToDir(c, tard, {}, {})
            
        return
    
    curs=getExCurs()
    if(len(curs)<1):
        return 
    tardf=fullCurTarDirFile()
    if(tardf[0] is None ):
        return 
    
    #dfile.tras2One(tarf, curs)
    dirToOne(curs,tardf[0])
    return

def exCurTar():
    df=fullCurTarDirFile()
    if(type(df) is not type([]) or len(df)<>2 or df[0] is None or df[1] is None):
         return
     
    dfile.extar2Dir(df[1], df[0])
    dfile.delete_file_folder(df[1])
    return 

def upgCur2Run():
    srcdir=fullCurTarDirFile()[0]
    if(srcdir is None):
        return
    
    tardir=rbcfg.apppath
    
    dfile.copyDirToDir(srcdir, tardir, {}, {})
    dfile.delete_file_folder(srcdir)
    return

def upgWorkMain():
    def dirCls(* dirs):
        for d in dirs:
            dfile.clsDir(d)
            
        return
    
    
    if(len(cfgvol.upgmsg['downloads'])<0):
        return
    bckwkpath=cfgvol.upg['workpath']['pctar']
    backupCurVol()
    
    integerCurDowns()
    # exCurTar()
    curDown2History()
    upgCur2Run()
    
    lvol=cfgvol.getLastOKVol()
    if(lvol is not None):
        cfgvol.upgmsg['curRunVol']=lvol
        cfgvol.upgmsg['downloads']=[]
        
    cfgvol.persistCfgVol()
    
    dirCls(cfgvol.upg['workpath']['pctar'],cfgvol.upg['workpath']['ptestex'],cfgvol.upg['workpath']['pworkex'])
    
    return