'''
Created on 2011-8-12

@author: Tanglh
'''

import os,sys

def cmdsRender1(ctx):
    ret=""
    if(ctx is None or "cmdnames" not in ctx):
        return ret
    
    for cmd in ctx["cmdnames"]: 
        ret+=cmdRender1(cmd,ctx)
        
    return ret

def cmdRender1(cmd,ctx):
    if(type(cmd) is type('')):
        return cmdRender1Str(cmd,ctx)
    if(type(cmd) is type([])):    
        return cmdsRender2(cmd,ctx)
    
    return ""

def cmdRender1Str(cmd,ctx):
  if cmd in ctx["cmds"]:
    ret="""<li class="level1">             
           <a href='%s' target="workFrame">%s</a><ul class="level2"></ul></li>"""         
    return ret % (ctx["cmds"][cmd]["url"],ctx["cmds"][cmd]["name"])

  return ""

def cmdsRender2(cmd,ctx):
    ret="<li class='level1'>%s<ul class='level2'>" % ctx["cmds"][cmd[0]]["name"]
    for c in cmd[1:]:
        ret+=cmdRender2(c,ctx)
        
    ret+="</ul></li>"    
    return ret

def cmdRender2(cmd,ctx):
    if(type(cmd) is type('')):
        return cmdRender2Str(cmd,ctx)
    if(type(cmd) is type([])):    
        return cmdsRender2(cmd,ctx)
    
    return ""

def cmdRender2Str(cmd,ctx):  
    if cmd in ctx["cmds"]:
       ret='<li><a href="%s" target="workFrame">%s</a></li>'
       return ret % (ctx["cmds"][cmd]["url"],ctx["cmds"][cmd]["name"])
    return ""