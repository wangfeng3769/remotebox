'''
Created on 2011-6-2

@author: Tanglh
'''

import string,os,sys,stat
import glob,shutil
import tarfile,gzip ,fnmatch

import cmdexe
import rblog.worklog as wlog
import rbconf.conff as conff
import rberror.Errors as errs

zipcmd=["/usr/bin/tar -C "," -c . | /usr/bin/gzip | /usr/bin/openssl bf-cbc -k \"","\" -out "]
azipcmd="/usr/bin/tar -C %s -c . | /usr/bin/gzip | /usr/bin/openssl bf-cbc -k \"%s\" -out %s"
azipcmd2="/usr/bin/tar -C %s -c . | /usr/bin/gzip | /usr/bin/openssl bf-cbc -k \"%s\" -out %s"
azipcmd1="tar -zcvf %s -C %s %s"

PTNPASSKEY="_pass_"
PTNREFUSEKEY="_refuse_"

def mkzipcmd(zcmd,**kwargs):
    if(3==len(zcmd)==len(kwargs)):
        ret=zcmd[0]+kwargs['srcf']
        ret+=zcmd[1]+kwargs['psw']
        ret+=zcmd[2]+kwargs['tarf']
        return ret
    
def mkAzipcmd(zcmd,*args):    
    ret=zcmd % args
    return ret;

def pyzip(*args):
    tar = tarfile.open(args[0], "w:gz")#tar = tarfile.open(args[2], "w:gz")
    tar.add(joinPath(args[1],args[2]),args[3])#tar.add(args[0])
    tar.close()
    
    return
    '''
    fsize=os.path.getsize(args[0])
    
    return fsize
    '''

def cmdzip(tarIndex,*args):
   if(len(args)>3 and args[3] is not None):
       fileRename(joinPath(args[1],args[2]),joinPath(args[1],args[3]))
       
   ret=cmdexe.runcmd(mkAzipcmd(azipcmd1,* args))
   #fsize="0000000000"+str(os.path.getsize(tarf))
   
   if(len(args)>3 and args[3] is not None):
       fileRename(joinPath(args[1],args[3]),joinPath(args[1],args[2]))
   return 

def dozip(tarIndex,*args):
    eval(conff.TRAN["zipper"])
    '''
   if("os" in conff.TRAN and conff.TRAN["os"]=="test"):
      pyzip(*args)
   else:
      cmdzip(tarIndex,*args)
   '''
    
   
    fsize=os.path.getsize(args[tarIndex])
    bsize=os.stat(args[tarIndex])[stat.ST_SIZE]
    msg="tarfile=%s  fsize=%s  bsize=%s" % (args[tarIndex],str(fsize),str(bsize))
    #print msg
    wlog.getLogger().debug(msg)
   
    return  fsize,bsize
def chkDir(dirName):
    if(not dirName or dirName==''):
        msg="error dirName:%s" % dirName
        wlog.getLogger().debug(msg)
        raise msg
def chkCreateDir(dirName):
    chkDir(dirName)
   
    if(os.path.exists(dirName)):
       return
    
    os.makedirs(dirName)
    return

def newDir(dirName):
    chkDir(dirName)
    
    if(os.path.exists(dirName)):
        delete_file_folder(dirName)

    os.makedirs(dirName)
    return
   
def delete_file_folder(src):
    '''delete files and folders'''
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            delete_file_folder(itemsrc) 
        try:
            os.rmdir(src)
        except:
            pass
        
def delFile(path,patten):
    ret=[]
    for src in glob.glob1(path, patten):
        sp=joinPath(path,src)
        if os.path.isfile(sp):
            try:
              os.remove(sp)
              ret.append(sp)
            except Exception,err:  
                wlog.getLogger().error("err for del file:%s by %s" % (sp,err.message))
    
    return ret

# after 0.8.7
def clsDir(dir):
    files=os.listdir(dir)
    for d in files: 
        src=joinPath(dir,d)  
        delete_file_folder(src)
        
    return

def existFile(path,mainfile,patten=".*"):
    if(type(mainfile)==type('') and type(path)==type('') ):
        nptn=mainfile+patten
        
        return len(glob.glob1(path, nptn))>0
    
    return False

def joinPath(base,joining):
    e1=base.endswith("/")
    s1=joining.startswith("/")
    
    if(e1==False and s1==False):
        return base+"/"+joining
    if(e1==True and s1==True):
        return base+joining[1:]
        
    return base+joining

def fileRename(old,new):
    try:
        os.rename(old, new)
    except Exception,err:  #after 0.8.8
        wlog.getLogger().error("ignor err for fileRename file:%s to %s" % (old,new))
        wlog.doTraceBack()        
                              
    return

#after 0.8.8
def renameFile(old,new):
    os.rename(old, new)
    return

def copyFileToDirs(src,* tag):
    if(type(src) is type('')):
        for t in tag:
            chkCreateDir(t)
            shutil.copy(src, t) 
    return 

# after 0.8.7
def copyDirToDir(src,ptar,dirMode={},fileMode={}): 
    def passDir(d):
        return passByPatten(d,** dirMode)
    
    def passFile(f):
        return passByPatten(f,** fileMode)
    
    def getModes(d):
        ret=[{},fileMode]
        if(d in dirMode):
            ret[0]=dirMode[d]
            
        return ret
    
    files=os.listdir(src)
    for d in files:       
       nsrc=joinPath(src,d )      
       if(os.path.isdir(nsrc) ):
           if(not passDir(d)):
               continue
           ntar=joinPath(ptar,d)
           chkCreateDir(ntar)
           copyDirToDir(nsrc,ntar , * getModes(d)) 
           continue
       
       if(not passFile(d)):
               continue
       copyFileToDirs(nsrc,ptar)
    return

def passByPatten(d, ** mod):
    def dotest(ret,d,* ptns):
        if(type(d)==type('')):
            for p in ptns:
                pok=fnmatch.fnmatchcase(d, p)
                if(pok<>ret):
                    return pok
                
        return ret
        
    def dopass(d, * ptns):
        return dotest(False,d,* ptns)
    '''
        pok=False
        if(type(d)==type('')):
            for p in ptns:
                pok=fnmatch.fnmatchcase(d, p)
                if(pok==True):
                    return pok
                
        return pok
    '''
    def dorefuse(d, * ptns):
        return dotest(True,d,* ptns)
    '''
        pok=True
        if(type(d)==type('')):
            for p in ptns:
                pok=fnmatch.fnmatchcase(d, p)
                if(pok==False):
                    return pok
                
        return pok
      '''         
    pok=True
    if(PTNPASSKEY in mod):
        pok=dopass(d, * mod[PTNPASSKEY])
        if(pok==True):
            return pok
        
    if(PTNREFUSEKEY in mod):
        pok=(not dorefuse(d , * mod[PTNREFUSEKEY]))
        
    return pok 

def ascFilesByTime(path , files):
    ret=[]
    nfiles=[(os.path.getmtime(path+x),x) for x in files]
    nfiles.sort()
    for v in nfiles:
        ret.append(v[1])
        
    return ret

def writeStreamToFile(data,tarf):
    tar = open(tarf, "wb")
    tar.write(data)
    
    tar.close()
    return

def appendStreamsToFile(tarf,datas=[]):
    tar = open(tarf, "ab")
    for data in datas:
        tar.write(data)
    
    tar.close()
    return

#after 0.8.7 
def tras2One(tarf,srcs=[]):
    tar = open(tarf, "ab")
    for f in srcs:
        ff=  open(f, "rb")
        data=ff.read()
        tar.write(data)
    
    tar.close()
    return

def extar2Dir(tarname,dirname):
    tar = tarfile.open(tarname, "r")
        
    tar.extractall(dirname)
    return

def tarADir(tarname,dirname,arcname):
    tar = tarfile.open(tarname, "w:gz")
    tar.add(dirname,arcname)
    
    return 