'''
Created on 2011-9-13

@author: Tanglh
'''

class RbErr(Exception):
    def __init__(self, value):
          self.value = value
          return
      
    def __str__(self):
          return repr(self.value)
      
class RbDBErr(RbErr):
    pass

class RbFtpErr(RbErr):
    pass

class RbRemoteErr(RbErr):
    pass

class RbFileErr(RbErr):
    pass

