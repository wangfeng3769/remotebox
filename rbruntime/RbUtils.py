'''
Created on 2011-8-10

@author: Tanglh
'''

import os,sys

def copyList(src):
    ret=[]
    if(type(src) is type(ret)):
        ret.extend(src)
        return ret
    
    return src
