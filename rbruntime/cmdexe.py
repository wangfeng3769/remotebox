'''
Created on 2011-6-1

@author: Tanglh
'''

import string,os,sys
import rblog.worklog as wlog

datatimecmd="date +%s000"
#[0:13]

reworksh={"rework":None,"upgrework":None}

def runcmd(cmd):
        fp=os.popen(cmd)
        # logger.debug("commandstr="+cmd)
        wlog.getLogger().debug("commandstr="+cmd)
        return fp.read()
