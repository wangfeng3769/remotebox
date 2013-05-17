'''
Created on 2011-9-19

@author: Tanglh
'''

import ftplib

import rbconf.conff as rbcfg
import rblog.worklog as wlog
import rbruntime.PoolUtils as poolutils
import rbruntime.dirfile as dirfile

class _FTPInnerPool(poolutils._InnerPool):
        def _newDB_(self):
            oftp=ftplib.FTP()
            oftp.connect(rbcfg.ftp['IP'],rbcfg.ftp['PORT'])
            oftp.login(rbcfg.ftp['USER'],rbcfg.ftp['PSW'])
            
            return oftp
    
        def _releaseDB_(self,ret):
            if(ret is None):
                return None
            
            ok= False
            try:
                ret.quit()
                ok =True
            except:
               wlog.doTraceBack() 
               
            if(ok == False):
                try:
                    ret.close()
                except:
                   wlog.doTraceBack() 
                
            ret=None
            
            return ret

class _FTPWrapPool(poolutils._WrapPool):
    def __init__(self,** karg):
        kkr=karg
        if 'BASE' not in kkr:kkr['BASE']=1
        if 'ATTEN' not in kkr:kkr['ATTEN']=1
        if 'REAL' not in kkr:kkr['REAL']=1
        if 'REALP' not in kkr:kkr['REALP']=1
        
        poolutils._WrapPool.__init__(self, _FTPInnerPool,** kkr)
        
        return
    
def FTPWrapPool():
    return _FTPWrapPool()

def existFile(ftpfile,localdir):    
    return dirfile.existFile(localdir, ftpfile)

def downFile(oftp,ftpfile,localfile):
    file_handler=open(localfile,'wb').write
    oftp.retrbinary('RETR '+ftpfile,file_handler,1024)
    
    return
    
def delFile(oftp,ftpfile):
    oftp.delete(ftpfile)
    
    return

ignors=[".LCK",".LOCK"]
def ignorFile(ftpf):
    if(type(ftpf) == type('')):
        if(ftpf==''):return True
        
        s=ftpf;s=s.upper()
        for v in ignors:
            if(s.endwith(v)):return True
            
    return False    

def ftpDowns(oftp,ftpdir,wkpath,funW,funF):
    if(oftp is None or funW is None or funF is None):return
    
    bn=dirfile.joinPath(wkpath, ftpdir)
    
    for ftpf in oftp.nlst():
        if(ignorFile(ftpf) or existFile(ftpf,wkpath)):continue
        localW=funW(bn)
        localF=funF(bn)
        
        try:
            downFile(oftp,ftpf,localW)
        except:
            wlog.doTraceBack()
            continue
        
        try:
            delFile(oftp,ftpf)
        except:
            wlog.doTraceBack()
            continue
        
        dirfile.fileRename(localW, localF)
        
    return

FTPPool=FTPWrapPool()
