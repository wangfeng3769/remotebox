'''
Created on 2012-4-11

@author: tanglh
after 0.8.7
'''
import rbruntime.dirfile as dfile

filefix={"down":".dn","cdown":".cdn","backup":".bck"}

bckfilemode={dfile.PTNREFUSEKEY:["*.pyc"]}
bckdirmode={dfile.PTNPASSKEY:["rb*","serial","workdatas"]
       ,"workdatas":{dfile.PTNPASSKEY:["www","rbconfig"]}}