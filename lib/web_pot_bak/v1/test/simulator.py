#encoding: utf8

import sys
sys.path.append('../')
import requests
import time
from functools import partial

def dictStr(d):
    return '&'.join(['%s=%s' % (k,d[k]) for k in d])

def http_test(url, dat):
    start = time.time()
    para = {}
    for k in dat:
        para[k] = dat[k].d
    print "URL:" + "%s?%s" % (url, dictStr(para))
    rslt = requests.get(url, params=para, verify=False)
    end = time.time()
    print "cost:", end - start
    return rslt

#prefix = "https://sandbox.api.wanhui.cn/v1/gate_machine/"
prefix = "http://10.77.134.201:10110/v1/gate_machine/"
#prefix = "http://10.77.135.213:10110/v1/gate_machine/"

#functions
enter_authen = partial(http_test, prefix + "enter_authen")
admittance = partial(http_test, prefix + "admittance")
exit_authen = partial(http_test, prefix + "exit_authen")
leave = partial(http_test, prefix + "leave")
reprint = partial(http_test, prefix + "reprint")
advertise = partial(http_test, prefix + "advertise")
get_privilege = partial(http_test, prefix + "get_privilege")
set_privilege = partial(http_test, prefix + "set_privilege")
get_room = partial(http_test, prefix + "get_room_info")
set_room = partial(http_test, prefix + "set_room_info")


#variables
class Data:
    def __init__(self, val):
        self.d = val


qpm1 = "30652194350623"
qpm2 = "72326735540406"
qpm3 = "32785371423043"

uid1 = "2012345678901234"
uid2 = "3012345678901234"
uid3 = "1012345678901234"

sceneNo =  Data("20150203183010068009")
mid = Data('11')
incode = Data("21403603159079")
ticketQr = Data('')
ticketNo = Data('')
ctcCode = Data('')
scanType = Data(2)
#1、条形码（暂无）
#2、二维码（含员工码、取票码、纸质票码）
#3、会员卡（射频卡）
#4、蓝牙

passType = Data(1)
#1 – 新入场
#2 – 返场
#3 – 员工

enterFlag = Data(1)
exitFlag = Data(1)
passType = Data(1)
period = Data(1)
ticketCode="32036211dEW7y18zyJRVSFc2nO2SqZGa9ImOPgqAOy86drn/6NlZFx9kNkkMoOhdTOgYJZ8EVqMIwMv4R/tqOSKWN9mhmOHapI3rftCLFxvVU0zMODv4m0NTDO3rDfkqfGXOazeMdJP0VGi8inqo3aEf5WuWhxWeIdFl6CPksO4qC45/zpI="
memberId = "60101010101010"

nfc = "123435216672|8888100008833515=000001000895598880"

checkData = {
        'mid': mid,
        'sceneNo': sceneNo,
        'type':  scanType,
        'code':  incode
        }

checkData2 = {
        'mid': '11',
        'sceneNo': "20150203183010068009",
        'type':  scanType,
        'code':  "43340153938026"
        }

admitData = {
        'mid': mid,
        'passType': passType,
        'ctcCode': ctcCode,
        'enterFlag': enterFlag,
        'sceneNo': sceneNo
        }


exitData = {
        'mid': mid,
        'type': scanType,
        'code': incode,
        'sceneNo': sceneNo
        }

leaveData = {
        'mid': mid,
        'ctcCode': incode,
        'exitFlag': exitFlag,
        'sceneNo': sceneNo
        }


reprintData = {
        'mid': mid,
        'type': scanType,
        'code': incode,
        'sceneNo': sceneNo
        }

timeData = {
        'mid': mid,
        'machine_time': '2015-01-07 21:00:00'
        }


scheData = {
        'mid': mid,
        'period': period
        }



