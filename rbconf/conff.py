'''
Created on 2011-6-7

@author: Tanglh
attendance
'''

import ConfigParser
import rblog.worklog as wlog

STSBARRIER={"DISBL":3,"AUTORUN":3}

'''
db={"DRIVER":'{SQL Server Native Client 10.0}',
    "SERVER":'172.16.0.12',
    "DATABASE":'test1',
    "UID":'sa',
    "PWD":'123456',
    "PAGESIZE":1000}

db={"DRIVER":'{SQL Server}',
    "SERVER":'172.16.0.200',
    "DATABASE":'intranet',
    "UID":'sa',
    "PWD":'123',
    "PAGESIZE":1000}
'''
db={"DATABASE":'intranet',"PAGESIZE":500}

ftp={'IP':'','PORT':8888,'USER':'','PSW':''}
#"zipper":"cmdzip(tarIndex,*args)",  "zipper":"pyzip(*args)", socktrans pytrans  "HeartBeat":["REALP","REAL"],
TRAN={"psw":'',"clsDir":True,"zipper":"pyzip(*args)","transmit":"socktrans","reboot":"rebootP","HeartBeat":["REALP"],
      "DTU":{},"Locator":"5321","DeviceCode":"1000000","DataFrom":"1","CAP":"DB","CTRLNO":None}
#172.16.0.59:8888  "REMOTE":("172.16.0.59",8888)

IMPLEMENTS={"BASE":{"PATH":"BASE/","TIMER":60,"REMOTE":("172.16.0.59",8888),"POOL":"BASE","CFGPRI":'ZAYHBSE_'},
           "ATTEN":{"PATH":"ATTEN/","TIMER":60,"REMOTE":("172.16.0.59",8888),"POOL":"ATTEN","CFGPRI":'ZAYHATN_'},
           "REAL":{"PATH":"REAL/","TIMER":60,"REMOTE":("172.16.0.59",8888),"POOL":"REAL","CFGPRI":'ZAYHRL_'},
           "REAL1":{"PATH":"REAL1/","TIMER":60,"REMOTE":("172.16.0.59",8888),"POOL":"REAL","CFGPRI":'ZAYHRL1_'},
           "REALP":{"PATH":"REALP/","TIMER":60,"REMOTE":("172.16.0.59",8888),"POOL":"REALP","CFGPRI":'ZAYHPTH_'}
           }
'''
IMPLEMENTS={"REAL":{"PATH":"REAL/","TIMER":60,"REMOTE":("172.16.0.59",8888),"POOL":"REAL","CFGPRI":'ZAYHRL_'},
           "REALP":{"PATH":"REALP/","TIMER":60,"REMOTE":("172.16.0.59",8888),"POOL":"REALP","CFGPRI":'ZAYHPTH_'}  
           }     

IMPLEMENTS={}  
'''
IMPLEMENTADDS={"ZAYHRPT":{"PATH":"SRPT/","TIMER":60,"REMOTE":("172.16.0.59",8888),"POOL":None,"CFGPRI":'ZAYHRPT_'}
           }

apppath="/"
basepath="/workdatas"
webroot="/www"
cfgpath="/rbconfig"

commcfg="common.conf"

'''
RUNMSG={"BASE":"OK",           "ATTEN":"OK",           "REAL":"OK",           "REAL1":"OK",           "REALP":"OK"}

# "OK" "FAIL_OPENTAR"  "FAIL_CON"  "FAIL_SEND"  "STOPED"  "RUNNING"  "RUNNED"
'''
RUNMSG={"COMM":"OK",
      "BASE":{"CMD":"OK","STS":"STOP","ERR":""},
           "ATTEN":{"CMD":"OK","STS":"STOP","ERR":""},
           "REAL":{"CMD":"OK","STS":"STOP","ERR":""},
           "REAL1":{"CMD":"OK","STS":"STOP","ERR":""},
           "REALP":{"CMD":"OK","STS":"STOP","ERR":""},
           "ZAYHRPT":{"CMD":"OK","STS":"STOP","ERR":""},
           }
def vtypeof(obj):
        return type(obj)
WEB={"port":5080,"urls":[],"refs":globals(),"uCkey":"user","auth":None,"authFUrl":"/TOPLOGIN"}#"refs":globals()
CONWEB={"arg":["index"],"karg":{},"render":"doRender"}
#{"arg":["showSts"],"karg":{"auth":WEB["auth"] },"render":"ctxRender"}
#print WEB["refs"]['vtypeof']

CONFIGCMDS={'CONSOLE':{'name':u'\u63a7\u5236\u53f0','status':0.0,"url":"/A/showSts"},
            'DEVCODE':{'name':u'\u8bbe\u5907\u7f16\u53f7','status':0.1}, #'\xc9\xe8\xb1\xb8\xb1\xe0\xba\xc5'
              'LOCAL':{'name':'\xb1\xbe\xbb\xfa\xc5\xe4\xd6\xc3'.decode("GBK"),'status':1},
              'FTP':{'name':'FTP \xc5\xe4\xd6\xc3'.decode("GBK"),'status':2.0},
              'DB':{'name':'\xca\xfd\xbe\xdd\xd4\xb4\xc5\xe4\xd6\xc3'.decode("GBK"),'status':2.0},
              'ZAYHRM':{'name':'\xce\xde\xcf\xdf\xb7\xa2\xcb\xcd\xc5\xe4\xd6\xc3'.decode("GBK")},
              'ZAYHBSE':{'name':'\xbb\xf9\xb4\xa1\xca\xfd\xbe\xdd\xc5\xe4\xd6\xc3'.decode("GBK"),'status':3.1},
              'ZAYHATN':{'name':'\xbf\xbc\xc7\xda\xc0\xe0\xca\xfd\xbe\xdd\xc5\xe4\xd6\xc3'.decode("GBK"),'status':3.2},
              'ZAYHRL':{'name':'\xca\xb5\xca\xb1\xca\xfd\xbe\xdd\xc5\xe4\xd6\xc3'.decode("GBK"),'status':3.3},
              'ZAYHRL1':{'name':'\xb1\xa8\xbe\xaf\xca\xfd\xbe\xdd\xc5\xe4\xd6\xc3'.decode("GBK"),'status':3.4},
              'ZAYHPTH':{'name':'\xb2\xb9\xb2\xee\xca\xfd\xbe\xdd\xc5\xe4\xd6\xc3'.decode("GBK"),'status':3.5},
              'ZAYHRPT':{'name':'\xd7\xb4\xcc\xac\xb1\xa8\xb8\xe6\xc5\xe4\xd6\xc3'.decode("GBK"),'status':3.6}}

def CMDFILTER_2_0(* arg):
    import cfgdb
    
    return cfgdb.filterByCfgKey(* arg)

def getCtrlNoStr():#1.0.0.1
    if("CTRLNO" not in TRAN ):
        return ""
    
    if(type(TRAN["CTRLNO"]) == type(0) and TRAN["CTRLNO"]>0):
       return str(TRAN["CTRLNO"])+"_"
   
    if(type(TRAN["CTRLNO"]) == type('') and len(TRAN["CTRLNO"])>0):# 1.0.0
       return TRAN["CTRLNO"]+"_"
   
    return ""

def getCtrlHead(): #1.0.0.1
    '''
    if("CTRLHEAD"  not in TRAN):
        TRAN["CTRLHEAD"]="ZA_CTRL_"+getCtrlNoStr()    
   
    return  TRAN["CTRLHEAD"]
    '''
    return "ZA_CTRL_"+getCtrlNoStr() 

def getDriverName():
    ret='{SQL Server}'
    if("SQLDRIVER" in db):
        ret= db["SQLDRIVER"]
        
    return ret
    

CMDCONS=['CONSOLE']
CMDFILTER={'0':['DEVCODE'],
           '1':['LOCAL'],
           '2':[(CMDFILTER_2_0,"LOCAL_CAPTYPE")],
           '3':['ZAYHBSE','ZAYHATN','ZAYHRL','ZAYHRL1','ZAYHPTH','ZAYHRPT']}
##'2':[(CMDFILTER_2_0,"LOCAL_CAPTYPE"),['ZAYHRM','ZAYHBSE','ZAYHATN','ZAYHRL','ZAYHRL1','ZAYHPTH','ZAYHRPT']]

CAPTYPES=["DB","FTP"]
ZALsnrFields={"DB":["_EBL","_IP","_PORT","_TIMER"],"FTP":["_EBL","_IP","_PORT","_TIMER","_FTPPATH"]}
ZALsnrPages=['ZAYHBSE','ZAYHATN','ZAYHRL','ZAYHRL1','ZAYHPTH']
CONFIGPAGES={'DEVCODE':["DEVCODE"],
              #'LOCAL':["LOCAL_IP","LOCAL_MASK","LOCAL_GATE","LOCAL_CAPTYPE","UPDATE_AUTO","UPDATE_IP","UPDATE_PORT","UPDATE_USER","UPDATE_PSW"],
              'LOCAL':["LOCAL_CAPTYPE","UPDATE_AUTO","UPDATE_TIME_H","UPDATE_TIME_M"],
              'FTP':["FTP_IP","FTP_PORT","FTP_USER","FTP_PSW"],#["FTP_IP","FTP_PORT","FTP_USER","FTP_PSW","FTP_PSW_R"]
              'DB':["DB_IP","DB_PORT","DB_USER","DB_PSW"],
              'ZAYHBSE':["ZAYHBSE_EBL","ZAYHBSE_IP","ZAYHBSE_PORT","ZAYHBSE_TIMER"],
              'ZAYHATN':["ZAYHATN_EBL","ZAYHATN_IP","ZAYHATN_PORT","ZAYHATN_TIMER"],
              'ZAYHRL':["ZAYHRL_EBL","ZAYHRL_IP","ZAYHRL_PORT","ZAYHRL_TIMER"],
              'ZAYHRL1':["ZAYHRL1_EBL","ZAYHRL1_IP","ZAYHRL1_PORT","ZAYHRL1_TIMER"],
              'ZAYHPTH':["ZAYHPTH_EBL","ZAYHPTH_IP","ZAYHPTH_PORT","ZAYHPTH_TIMER"],
              'ZAYHRPT':["ZAYHRPT_EBL","ZAYHRPT_IP","ZAYHRPT_PORT","ZAYHRPT_TIMER"]}

def freshCfgPageFields(cpg,ftype):
    if(cpg in CONFIGPAGES and ftype in ZALsnrFields):
        ret=[]
        for v in ZALsnrFields[ftype]:
            ret.append(cpg+v)
            
        CONFIGPAGES[cpg]=ret
    return

def freshCfgLsnrPages():
    ftype=CAPTYPES[0]
    if(TRAN["CAP"] in ZALsnrFields):
        ftype=TRAN["CAP"]
        
    for lp in ZALsnrPages:
       freshCfgPageFields(lp,ftype) 
       
    return 


CONFIGPagePriTpl={'FTP':{'pri':"FTP_","tpl":"DataSource"},
              'DB':{'pri':"DB_","tpl":"DataSource"},
              'ZAYHBSE':{'pri':"ZAYHBSE_","tpl":"ZALsnr"},
              'ZAYHATN':{'pri':"ZAYHATN_","tpl":"ZALsnr"},
              'ZAYHRL':{'pri':"ZAYHRL_","tpl":"ZALsnr"},
              'ZAYHRL1':{'pri':"ZAYHRL1_","tpl":"ZALsnr"},
              'ZAYHPTH':{'pri':"ZAYHPTH_","tpl":"ZALsnr"},
              'ZAYHRPT':{'pri':"ZAYHRPT_","tpl":"ZALsnr"}}

CONFIGITEMS={"DEVCODE":('\xc9\xe8\xb1\xb8\xb1\xe0\xba\xc5'.decode("GBK"),
                        '11\xce\xbb\xb6\xa8\xb3\xa4\xd0\xf2\xc1\xd0\xc2\xeb\xa3\xac\xb3\xf5\xca\xbc\xd6\xb5\xa3\xba00000000000'.decode("GBK")),
             "LOCAL_IP":('\xb1\xbe\xbb\xfaIP\xb5\xd8\xd6\xb7'.decode("GBK")
                         ,'\xc7\xeb\xc1\xaa\xcf\xb5\xc3\xba\xbf\xf3\xb5\xc4\xb9\xdc\xc0\xed\xd4\xb1'.decode("GBK")),
             "LOCAL_MASK":('\xd7\xd3\xcd\xf8\xd1\xda\xc2\xeb'.decode("GBK"),
                           '\xc7\xeb\xc1\xaa\xcf\xb5\xc3\xba\xbf\xf3\xb5\xc4\xb9\xdc\xc0\xed\xd4\xb1'.decode("GBK")),
             "LOCAL_GATE":('\xb1\xbe\xbb\xfa\xc2\xb7\xd3\xc9'.decode("GBK"),
                           '\xd3\xc3GPRS/CDMA\xca\xb1\xb2\xbb\xbd\xa8\xd2\xe9\xc9\xe8\xd6\xc3\xa3\xac\xd6\xb1\xbd\xd3\xd3\xc3\xcd\xf8\xcf\xdf\xbd\xf8\xd0\xd0\xc1\xac\xbd\xd3\xb5\xc4\xca\xb1\xba\xf2\xd0\xe8\xd2\xaa\xc9\xe8\xd6\xc3'.decode("GBK")),
             "LOCAL_CAPTYPE":('\xca\xfd\xbe\xdd\xbb\xf1\xc8\xa1\xb7\xbd\xca\xbd'.decode("GBK"),''),
             "FTP_IP":('IP','FTP\xb7\xfe\xce\xf1\xc6\xf7\xb5\xc4IP'.decode("GBK")),
             "FTP_PORT":('\xb6\xcb\xbf\xda'.decode("GBK"),'FTP\xb7\xfe\xce\xf1\xc6\xf7\xb5\xc4\xb6\xcb\xbf\xda'.decode("GBK")),
             "FTP_USER":('\xc1\xac\xbd\xd3\xd5\xcb\xbb\xa7'.decode("GBK"),''),
             "FTP_PSW":('\xc3\xdc\xc2\xeb'.decode("GBK"),''),
             "FTP_PSW_R":('\xc8\xb7\xc8\xcf\xc3\xdc\xc2\xeb'.decode("GBK"),''),
             "DB_IP":('IP','\xca\xfd\xbe\xdd\xbf\xe2\xb7\xfe\xce\xf1\xc6\xf7\xb5\xc4IP'.decode("GBK")),
             "DB_PORT":('\xb6\xcb\xbf\xda'.decode("GBK"),'\xca\xfd\xbe\xdd\xbf\xe2\xb7\xfe\xce\xf1\xc6\xf7\xb5\xc4\xb6\xcb\xbf\xda'.decode("GBK")),
             "DB_USER":('\xc1\xac\xbd\xd3\xd5\xcb\xbb\xa7'.decode("GBK"),''),
             "DB_PSW":('\xc3\xdc\xc2\xeb'.decode("GBK"),''),
             "DB_PSW_R":('\xc8\xb7\xc8\xcf\xc3\xdc\xc2\xeb'.decode("GBK"),''),
             "ZAYHBSE_EBL":('\xc6\xf4\xd3\xc3'.decode("GBK"),''),
             "ZAYHBSE_IP":('IP','\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xbb\xf9\xb4\xa1\xca\xfd\xbe\xdd\xb5\xc4IP'.decode("GBK")),
             "ZAYHBSE_PORT":('\xb6\xcb\xbf\xda'.decode("GBK"),
                             '\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xbb\xf9\xb4\xa1\xca\xfd\xbe\xdd\xb5\xc4\xb6\xcb\xbf\xda'.decode("GBK")),
             "ZAYHBSE_TIMER":('\xc2\xd6\xd1\xaf\xd6\xdc\xc6\xda'.decode("GBK"),
                              '\xbb\xf1\xc8\xa1\xbb\xf9\xb4\xa1\xca\xfd\xbe\xdd\xb5\xc4\xbc\xe4\xb8\xf4\xd6\xdc\xc6\xda\xa3\xac\xb5\xa5\xce\xbb\xc3\xeb\xa3\xac\xc8\xb1\xca\xa1\xce\xaa3000'.decode("GBK")),
             "ZAYHATN_EBL":('\xc6\xf4\xd3\xc3'.decode("GBK"),''),
             "ZAYHATN_IP":('IP','\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xbf\xbc\xc7\xda\xc0\xe0\xca\xfd\xbe\xdd\xb5\xc4IP'.decode("GBK")),
             "ZAYHATN_PORT":('\xb6\xcb\xbf\xda'.decode("GBK"),
                             '\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xbf\xbc\xc7\xda\xc0\xe0\xca\xfd\xbe\xdd\xb5\xc4\xb6\xcb\xbf\xda'.decode("GBK")),
             "ZAYHATN_TIMER":('\xc2\xd6\xd1\xaf\xd6\xdc\xc6\xda'.decode("GBK"),
                 '\xbb\xf1\xc8\xa1\xbf\xbc\xc7\xda\xc0\xe0\xca\xfd\xbe\xdd\xb5\xc4\xbc\xe4\xb8\xf4\xd6\xdc\xc6\xda\xa3\xac\xb5\xa5\xce\xbb\xc3\xeb\xa3\xac\xc8\xb1\xca\xa1\xce\xaa3000'.decode("GBK")),
             "ZAYHRL_EBL":('\xc6\xf4\xd3\xc3'.decode("GBK"),''),
             "ZAYHRL_IP":('IP','\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xca\xb5\xca\xb1\xca\xfd\xbe\xdd\xb5\xc4IP'.decode("GBK")),
             "ZAYHRL_PORT":('\xb6\xcb\xbf\xda'.decode("GBK"),
                            '\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xca\xb5\xca\xb1\xca\xfd\xbe\xdd\xb5\xc4\xb6\xcb\xbf\xda'.decode("GBK")),
             "ZAYHRL_TIMER":('\xc2\xd6\xd1\xaf\xd6\xdc\xc6\xda'.decode("GBK"),
                 '\xbb\xf1\xc8\xa1\xca\xb5\xca\xb1\xca\xfd\xbe\xdd\xb5\xc4\xbc\xe4\xb8\xf4\xd6\xdc\xc6\xda\xa3\xac\xb5\xa5\xce\xbb\xc3\xeb\xa3\xac\xc8\xb1\xca\xa1\xce\xaa60'.decode("GBK")),
             "ZAYHRL1_EBL":('\xc6\xf4\xd3\xc3'.decode("GBK"),''),
             "ZAYHRL1_IP":('IP','\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xb1\xa8\xbe\xaf\xca\xfd\xbe\xdd\xb5\xc4IP'.decode("GBK")),
             "ZAYHRL1_PORT":('\xb6\xcb\xbf\xda'.decode("GBK"),
                  '\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xb1\xa8\xbe\xaf\xca\xfd\xbe\xdd\xb5\xc4\xb6\xcb\xbf\xda'.decode("GBK")),
             "ZAYHRL1_TIMER":('\xc2\xd6\xd1\xaf\xd6\xdc\xc6\xda'.decode("GBK"),
                '\xbb\xf1\xc8\xa1\xb1\xa8\xbe\xaf\xca\xfd\xbe\xdd\xb5\xc4\xbc\xe4\xb8\xf4\xd6\xdc\xc6\xda\xa3\xac\xb5\xa5\xce\xbb\xc3\xeb\xa3\xac\xc8\xb1\xca\xa1\xce\xaa60'.decode("GBK")),
             "ZAYHPTH_EBL":('\xc6\xf4\xd3\xc3'.decode("GBK"),''),
             "ZAYHPTH_IP":('IP',
                '\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xca\xb5\xca\xb1\xbb\xf2\xb1\xa8\xbe\xaf\xb5\xc4\xb2\xb9\xb2\xee\xca\xfd\xbe\xdd\xb5\xc4IP'.decode("GBK")),
             "ZAYHPTH_PORT":('\xb6\xcb\xbf\xda'.decode("GBK"),
                '\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xca\xb5\xca\xb1\xbb\xf2\xb1\xa8\xbe\xaf\xb5\xc4\xb2\xb9\xb2\xee\xca\xfd\xbe\xdd\xb5\xc4\xb6\xcb\xbf\xda'.decode("GBK")),
             "ZAYHPTH_TIMER":('\xc2\xd6\xd1\xaf\xd6\xdc\xc6\xda'.decode("GBK"),
                '\xbb\xf1\xc8\xa1\xca\xb5\xca\xb1\xbb\xf2\xb1\xa8\xbe\xaf\xb5\xc4\xb2\xb9\xb2\xee\xca\xfd\xbe\xdd\xb5\xc4\xbc\xe4\xb8\xf4\xd6\xdc\xc6\xda\xa3\xac\xb5\xa5\xce\xbb\xc3\xeb\xa3\xac\xc8\xb1\xca\xa1\xce\xaa60'.decode("GBK")),
             "ZAYHRPT_EBL":('\xc6\xf4\xd3\xc3'.decode("GBK"),''),
             "ZAYHRPT_IP":('IP','\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xd7\xb4\xcc\xac\xb1\xa8\xb8\xe6\xb5\xc4IP'.decode("GBK")),
             "ZAYHRPT_PORT":('\xb6\xcb\xbf\xda'.decode("GBK"),
                '\xca\xfd\xbe\xdd\xd6\xd0\xd0\xc4\xbd\xd3\xca\xd5\xd7\xb4\xcc\xac\xb1\xa8\xb8\xe6\xb5\xc4\xb6\xcb\xbf\xda'.decode("GBK")),
             "ZAYHRPT_TIMER":('\xc2\xd6\xd1\xaf\xd6\xdc\xc6\xda'.decode("GBK"),
                '\xbb\xf1\xc8\xa1\xd7\xb4\xcc\xac\xb1\xa8\xb8\xe6\xb5\xc4\xbc\xe4\xb8\xf4\xd6\xdc\xc6\xda\xa3\xac\xb5\xa5\xce\xbb\xc3\xeb\xa3\xac\xc8\xb1\xca\xa1\xce\xaa60'.decode("GBK"))}

STATIC_PRI=['/static/',"/images/"]  #STATIC_PRI=['/static/',"/images/","/js/"]

def isStaticPri(url):
    if(type(url) is type('')):
        for hd in STATIC_PRI:
            if(type(hd) is type('') and url.startswith(hd)):
                return True
            
    return False

def getConf():
    cf=ConfigParser.ConfigParser()
    cf.read("comm.conf")
    
    return cf;

def freshImpTypes(**karg):
    if(karg=={}):return
    for k in IMPLEMENTS.keys():
        if(k not in karg):
            IMPLEMENTS.pop(k)
            
    return

def freshRunCmd():
    for k in RUNMSG.keys():
        if(k=="COMM" or k in IMPLEMENTADDS):continue
        
        if(k not in IMPLEMENTS):RUNMSG.pop(k)
        
    return   

def freshCMDFILTER(**karg):
    for k in karg:
        CMDFILTER[k]=karg[k]
        
    return