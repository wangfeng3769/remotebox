'''
Created on 2011-6-13

@author: Tanglh

hear defined all pojos fields,field's parse
'''

import os,sys,datetime
# after 0.8.5
import rbdatabase
import DBFactory,PojoBuilder
import rblog.worklog as wlog
import rbaction.BaseAction as baction
import rbconf.conff as rbcfg 

ctrlDef={"BASE":{"ctrl":DBFactory.CtrlTB4Base,
                 "pjcap":PojoBuilder.DBCaptrue,
                 "lstp":baction.ListParse,
                 "wfile":baction.StrLstWriteFile},
         "ATTEN":{"ctrl":DBFactory.CtrlTB4BaseD,
                 "pjcap":PojoBuilder.DBCaptrue,
                 "lstp":baction.ListParse,
                 "wfile":baction.StrLstWriteFile},
         "REAL":{"ctrl":DBFactory.CtrlTB4Real,
                 "pjcap":PojoBuilder.DBCaptrue,
                 "lstp":baction.ListParse,
                 "wfile":baction.StrLstWriteFile},
         "REALP":{"ctrl":DBFactory.CtrlTB4RealP,
                 "pjcap":PojoBuilder.DBCaptrue,
                 "lstp":baction.ListParse,
                 "wfile":baction.StrLstWriteFile}
         }

specialCtrlDefName={"REAL1":"REAL","REALP":"REALP"}

PjRYSJ={"fields":["UID","MineID","StafferID","CardID","IfStop","Occupation","WorkType","Department","StafferLevel","BanType","StafferName","CertificateID","Birth","WorkAddress","CardMode","PinYin","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','Date1'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'RYSJ'}#UploadStaffer

PjBZSZ={"fields":["UID","MineID","BanTypeID","BanTypeName","FullMinute","HalfMinute","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'BZSZ'}#UploadBanType 

PjBCSZ={"fields":["UID","MineID","BanID","BanName","BanTypeID","StartTime","EndTime","StartTimeExt","EndTimeExt","LateTime","EarlyTime","AddTime","DateOffset","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','Time1'],['datetime','Time1'],['datetime','Time1'],['datetime','Time1'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'BCSZ'}#UploadBanDefine #banci

'''
PjGZXX={"fields":["UID","MineID","WorkID","WorkName","WorkValue","WorkClass","LevelNormal","LevelOver","LevelSerious","WorkRank","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'GZXX'}#UploadWorkType #gongzhong
'''
PjGZXX={"fields":["UID","MineID","WorkID","WorkName","LevelNormal","LevelOver","LevelSerious","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'GZXX'}#UploadWorkType #gongzhong

PjGWXX={"fields":["UID","MineID","OctID","OctName","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'GWXX'}#UploadOccupation #gangwei

PjBMXX={"fields":["UID","MineID","DeptID","DeptName","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'BMXX'}#UploadDepartment #bumenxinxi

PjJBGL={"fields":["UID","MineID","LevelID","LevelName","Ifupdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'JBGL'}#UploadStafferLevel #jibieguanli

#["UID","MineID","MapID","MapName","MapData","IsCad","EnteringTime"],  ["UID","MineID","MapID","MapName","MapData","IsCad","Scale","MapInfo","Ifupdate","EnteringTime"],
PjDTXX={"fields":["UID","MineID","MapID","MapName","IsCad","Scale","MapInfo","Ifupdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'DTXX'}#UploadMapList #dituxinxi

PjQYXX={"fields":["UID","MineID","AreaID","AreaName","AreaType","AreaPlanPeople","StayMinute","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'QYXX'}#UploadAreaInfo #quyubiao

PjDWSB={"fields":["UID","MineID","AreaID","StationID","StationName","StationType","StationProperty","X","Y","Z","StationPosition","GasIgnore","GasValue","MapID","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'DWSB'}#UploadStationInfo #dingweishebei

PjTZYS={"fields":["UID","MineID","RouteIndex","StafferID","StationID","RequireTime","StationType","RequireMinute","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','Time1'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'TZYS'}#UploadSpecialTime #tedingrenyuanluxian

PjDBJH={"fields":["UID","MineID","StafferID","PlanDate","BantypeID","JHBanID","PlanStartTime","PlanEndTime","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','Time1'],['datetime','Time1'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'DBJH'}#UploadDownPlan #daibanjihua

PjKQJL={"fields":["UID","MineID","StafferID","KQTime","DownTime","UpTime","DownStationID","UpStationID","BanTypeID","BanID","CardID","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['datetime','DateTime22'],['datetime','DateTime22'],['datetime','DateTime22'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"ATTEN",
        "dtfield":'EnteringTime',
        "delWhere":None, #None ,# None  "  and (DownTime is not Null and  UpTime is not Null)",
        "file":'KQJL'}#UploadAttendance #kaoqingjilu

PjFZTL={"fields":["UID","MineID","StafferID","CardID","InTime","OutTime","WorkTime","AreaID","StationID","StationType","X","Y","Z","MapID","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['datetime','DateTime22'],['datetime','DateTime22'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"ATTEN",
        "dtfield":'EnteringTime',
        "delWhere":None, #"",
        "file":'FZTL'}#UploadStayInterval #shebeitingliu

PjWJJC={"fields":["UID","MineID","JCBID","GasConcentration","RecordTime","StationID","StationType","X","Y","Z","MapID","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"REAL",
        "dtfield":'EnteringTime',
        "delWhere":None, #"",# "" None
        "file":'WJJC'}#UploadGasData #wajianyijian

PjSSDW={"fields":["UID","MineID","CardID","StafferID","DownFlag","StationID","StationType","X","Y","Z","MapID","EnterTime","AreaID","EnterAreaTime","DownTime","UpTime","EnteringTime"],
        "fieldsdef":[['simple'],['simpleP'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10'],['simple'],['datetime','DateTime10'],['datetimeP','DateTime10'],['datetime','DateTime10'],['datetime','DateTime10']],
        "ctrlc":"REAL",
        "dtfield":'EnteringTime',
        "delWhere":None, #None,# "" None
        "file":'SSDW'}#UploadLocateData #shishirenyuan

PjXTYC={"fields":["UID","MineID","StationID","StationType","ExceptName","StartTime","EndTime","X","Y","Z","MapID","EnteringTime"],
        "fieldsdef":[['simple'],['simpleP'],['simple'],['simple'],['simple'],['datetime','DateTime10'],['datetime','DateTime10'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"REAL",
        "dtfield":'EnteringTime',
        "delWhere":None, #"",# "" None
        "file":'XTYC'}#UploadSystemError #xitonggongzuoyichang

PjCSBJ={"fields":["UID","MineID","StafferID","DownTime","StayMinute","PlanTimeEachClass","AlarmType","AlarmStartTime","AlarmEndTime","AreaID","EnterAreaTime","StationID","StationType","EnterTime","EnteringTime"],														
        "fieldsdef":[['simple'],['simpleP'],['simple'],['datetime','DateTime10'],['simple'],['simple'],['simple'],['datetime','DateTime10'],['datetime','DateTime10'],['simple'],['datetime','DateTime10'],['simple'],['simple'],['datetime','DateTime10'],['datetime','DateTime10']],	
        "ctrlc":"REAL",
        "dtfield":'EnteringTime',
        "delWhere":None, #"",# "" None
        "file":'CSBJ'}#UploadAlarmTime #chaoshibaojing

PjCYBJ={"fields":["UID","MineID","StafferID","AreaPlanPeople","PlanMiner","AlarmType","AlarmStartTime","AlarmEndTime","AreaID","EnterAreaTime","StationID","StationType","AreaSum","MineSum","EnteringTime"],
        "fieldsdef":[['simple'],['simpleP'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10'],['datetime','DateTime10'],['simple'],['datetime','DateTime10'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"REAL",
         "dtfield":'EnteringTime',
        "delWhere":None, #"",# "" None
        "file":'CYBJ'}#UploadAlarmPeople #chaoyuanbaojing  error

PjTZYC={"fields":["UID","MineID","StafferID","DownTime","AlarmStartTime","AlarmEndTime","AreaID","EnterAreaTime","StationID","StationType","EnterTime","AreaSum","Ptime","State","Atime","EnteringTime"],
        "fieldsdef":[['simple'],['simpleP'],['simple'],['datetime','DateTime10'],['datetime','DateTime10'],['datetime','DateTime10'],['simple'],['datetime','DateTime10'],['simple'],['simple'],['datetime','DateTime10'],['simple'],['datetime','DateTime10'],['simple'],['datetime','DateTime10'],['datetime','DateTime10']],
        "ctrlc":"REAL",
        "dtfield":'EnteringTime',
        "delWhere":None, #"",# "" None
        "file":'TZYC'}#UploadAlarmSpecial #tedingrenyuanyichang

PjHJXX={"fields":["UID","MineID","StafferID","DownTime","AlarmStartTime","AlarmEndTime","AreaID","EnterAreaTime","StationID","StationType","EnterTime","EnteringTime"],
        "fieldsdef":[['simple'],['simpleP'],['simple'],['datetime','DateTime10'],['datetime','DateTime10'],['datetime','DateTime10'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10'],['datetime','DateTime10']],
        "ctrlc":"REAL",
         "dtfield":'EnteringTime',
        "delWhere":None, #"",# "" None
        "file":'HJXX'}#UploadAlarmcall #hujiu
'''
PjWSBJ={"fields":["MineID","StafferID","DownTime","StayMinute","PlanTimeEachClass","AlarmType","AlarmStartTime","AlarmEndTime","AreaID","EnterAreaTime","StationID","StationType","EnterTime","EnteringTime"],
        "fieldsdef":[['simpleP'],['simple'],['datetime','DateTime10'],['simple'],['simple'],['simple'],['datetime','DateTime10'],['datetime','DateTime10'],['simple'],['datetime','DateTime10'],['simple'],['simple'],['datetime','DateTime10'],['datetime','DateTime10']],
        "ctrlc":"REAL",
         "dtfield":'EnteringTime',
        "delWhere":None, #"",# "" None
        "file":'WSBJ'}#UploadAlarmGas #wasibaojing
'''
PjWSBJ={"fields": ["UID","MineID","JCBID","AlarmType","MineGasValue","StationGasValue","GasConcentration","AreaID","StationID","StationType","X","Y","Z","MapID","EnteringTime"],
        "fieldsdef":[['simple'],['simpleP'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'], ['datetime','DateTime10']],
        "ctrlc":"REAL",
         "dtfield":'EnteringTime',
        "delWhere":None, #"",# "" None
        "file":'WSBJ'}#UploadAlarmGas #wasibaojing

'''
PjDep={"fields":["UID","MineID","DeptID","DeptName","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"BASE",
        "dtfield":'EnteringTime',
        "delWhere":None, #" and IfUpdate=99  ",
        "file":'UploadDepartment'}#bumenxinxi

PjUploadAttendance={"fields":["UID","MineID","StafferID","KQTime","DownTime","UpTime","DownStationID","UpStationID","BanTypeID","BanID","CardID","IfUpdate","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['datetime','DateTime10'],['datetime','DateTime10'],['datetime','DateTime10'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10']],
        "ctrlc":"ATTEN",
        "dtfield":'EnteringTime',
        "delWhere":None, #"  and (DownTime is not Null and  UpTime is not Null)",
        "file":'UploadAttendance'}#kaoqingjilu

PjLocateData={"fields":["MineID","CardID","StafferID","DownFlag","StationID","StationType","X","Y","Z","MapID","EnterTime","AreaID","EnterAreaTime","DownTime","UpTime","EnteringTime"],
        "fieldsdef":[['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['simple'],['datetime','DateTime10'],['simple'],['datetime','DateTime10'],['datetime','DateTime10'],['datetime','DateTime10'],['datetime','DateTime10']],
        "ctrlc":"REAL",
        "dtfield":'EnteringTime',
        "delWhere":None, #"",
        "file":'UploadLocateData'}#shishirenyuan
'''

pojonames={"BASE":["UploadStaffer","UploadBanType","UploadBanDefine","UploadWorkType","UploadOccupation","UploadDepartment","UploadStafferLevel","UploadMapList","UploadAreaInfo","UploadStationInfo","UploadSpecialTime","UploadDownPlan"],
           #"UploadStaffer","UploadBanType","UploadBanDefine","UploadWorkType","UploadOccupation","UploadDepartment","UploadStafferLevel","UploadMapList","UploadAreaInfo","UploadStationInfo","UploadSpecialTime","UploadDownPlan"
           "ATTEN":["UploadAttendance","UploadStayInterval"],# "UploadAttendance","UploadStayInterval"
           "REAL":["UploadGasData","UploadLocateData"],#"UploadGasData","UploadLocateData"
           "REAL1":["UploadSystemError","UploadAlarmTime","UploadAlarmPeople","UploadAlarmSpecial","UploadAlarmcall","UploadAlarmGas"],#"UploadSystemError","UploadAlarmTime","UploadAlarmPeople","UploadAlarmSpecial","UploadAlarmcall","UploadAlarmGas"
           #"UploadGasData","UploadLocateData","UploadSystemError","UploadAlarmTime","UploadAlarmPeople","UploadAlarmSpecial","UploadAlarmcall","UploadAlarmGas"
           #"REALP":[]#["UploadLocateData","UploadAlarmTime"]
           }

WorkPojos={}

#pojonames["REALP"].extend(pojonames["REAL"])
#pojonames["REALP"].extend(pojonames["REAL1"])

pojos={"UploadStaffer":PjRYSJ,       "UploadBanType":PjBZSZ,       "UploadBanDefine":PjBCSZ,       "UploadWorkType":PjGZXX,       "UploadOccupation":PjGWXX,
       "UploadDepartment":PjBMXX,       "UploadStafferLevel":PjJBGL,       "UploadMapList":PjDTXX,       "UploadAreaInfo":PjQYXX,       "UploadStationInfo":PjDWSB,
       "UploadSpecialTime":PjTZYS,       "UploadDownPlan":PjDBJH,       "UploadAttendance":PjKQJL,       "UploadStayInterval":PjFZTL,       "UploadGasData":PjWJJC,
       "UploadLocateData":PjSSDW,       "UploadSystemError":PjXTYC,       "UploadAlarmTime":PjCSBJ,       "UploadAlarmPeople":PjCYBJ,       "UploadAlarmSpecial":PjTZYC,
       "UploadAlarmcall":PjHJXX,       "UploadAlarmGas":PjWSBJ}

def freshRealP(* key):
    pojonames["REALP"]=[]
    for k in set(key) & set(pojonames.keys()):
           pojonames["REALP"].extend(pojonames[k])
           
    wlog.getExLogger(rbdatabase.logTag).debug(str(pojonames["REALP"]))
    return

def freshWorkPojos(**karg):
    #print "freshWorkPojos",karg
    global WorkPojos
    if(karg=={}):
        WorkPojos=pojonames
        return
    
    for k in karg:
        WorkPojos[k]=[]
        for n in karg[k]:
            WorkPojos[k].extend(pojonames[n])
    #print "freshWorkPojos",WorkPojos        
    return

# up 0.8.3
toryishes=["UploadAttendance","UploadStayInterval","UploadAlarmGas","UploadLocateData"]
def inToryishes(item):
    return item in toryishes