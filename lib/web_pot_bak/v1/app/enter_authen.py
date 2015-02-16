#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, threading, time, datetime, traceback
import random, urllib2, json

import web
from common_def import *
from encrypt import *
import requests
import server_conf as conf
import pass_record_check
import sql_cmd_gen

__MOCK__ = False

__MOCK_TICKETE_DATA__ = {u'ticket_info': {u'ticketStatus': u'1', u'serviceChargeValue': u'0.00', u'fee': u'0.00', u'startTime': u'2015-01-14 22:25:00', u'sellTime': u'2015-01-13 20:19:06', u'column': u'12', u'showNum': u'1', u'according': u'1', u'seller': u'web_dx', u'date': u'2015-01-14', u'cinemaName': u'\u5357\u4eac\u65b0\u8857\u53e3\u4e07\u8fbe\u5e7f\u573a\u5e97', u'qrCode': u'32036211fEW7y18zyJRVSFc2nO2SqZGa9ImOPgqAOy86drn/6NlZFx9kNkkMoOhdTOgYJZ8EVqMIwMv4R/tqOSKWN9mhmOHapI3rftCLFxvVU0zMODv4m0NTDO3rDfkqfGXOazeMdJP0VGi8inqo3aEf5WuWhxWeIdFl3000000000001058', u'ticketNum': u'3000000000001058', u'cinemaTicketCenterFlag': u'17332581242932', u'hallName': u'2\u53f7\u5385', u'seatId': u'7351', u'movieName': u'\u4e00\u751f\u6709\u4f60(\u56fd\u8bed)', u'price': u'70.00', u'ticketType': u'\u7f51\u8d2d\u7968', u'row': u'8'}, u'ticket_no': u'3000000000001058', u'cinema_name': u'\u5357\u4eac\u65b0\u8857\u53e3\u4e07\u8fbe\u5e7f\u573a\u5e97', u'led_light': 3, u'lcd_content': u'欢迎光临', u'allow_admission_flag': 0, u'gate_voice': 1, u'print_flag': 0}


AUTHEN_LCD_CONTENT = {
                      8: u'欢迎返场',
                      9: u'此票未正常出闸机',
                      401: u'该飞凡用户未购该场次的影票或影票失效',
                      402: u''
                     }

class enter_authen(object) :
    SCAN_TYPE_BAR_CODE = 1
    SCAN_TYPE_QR_CODE = 2
    SCAN_TYPE_MEMBER_CARD = 3
    SCAN_TYPE_BLUETOOTH =4

    class QueryData(object):
        def __init__(self):
            self.mid = ""
            self.type = 0
            self.code = ""
            self.sceneNo = ""
            self.codeMd5 = ""
            self.cinemaNo = ""
            self.roomNo = ""
            self.dingxinNo = ""
            self.filmCompanyNo = ""
            self.reqType = 0
            self.uid = '0'  #user id  = ff_member_id

    def __init__(self) :
        pass

    def __returnData(self, result_data) :
        try :
            self.end_time = time.time()

        except Exception, e:
            exception_info = "Exception(%s), traceback_data(%s)" % (str(e), traceback.format_exc())
            printlog("Error", "Return fail", "%s" % (exception_info))

        finally :
            printlog("Log", "Server Return", result_data)
            return result_data + "\n"


    def __makeWelcomeBackRslt(self, result_data, ctcCode):
        data = {}
        data['pass_type'] = 2
        data['ticket_info'] = {}
        data['ticket_no'] = ''
        data['ctcCode'] = ctcCode
        data['print_flag'] = 0
        data['allow_admission_flag'] = 0
        data['lcd_content'] = AUTHEN_LCD_CONTENT[8]
        result_data.status = 0
        result_data.substatus = 0
        result_data.message = "success"
        result_data.other_info = ""
        result_data.data = data


    def GET(self, inner_url):
        result_data = return_data()
        beg_time = time.time()

        try :
            input_storage = web.input()
            input_post_str = web.data()
            input_ctx_dict = web.ctx

            printlog("Log", "GET Params ok", "inner_url : %s" % (str(inner_url)))
            printlog("Log", "GET Params ok", "input_storage : %s" % (str(input_storage)))
            printlog("Log", "GET Params ok", "input_post_str : %s" % (str(input_post_str)))

            checkRslt, msg =  ParaCheck(input_storage, 'mid', 'type', 'code', 'sceneNo')
            if not checkRslt:
                result_data.status = 400
                raise Exception("bad params:" + msg)


            #sql = 'select machine_id, cinema_no, room_no, dingxin_no, film_campany_no from %s where machine_id="%s"' % (conf.TABLE_NAME_SCHEDULE, input_storage.mid)
            cols = ['machine_id', 'cinema_no', 'room_no', 'dingxin_no', 'film_campany_no']
            cond = {'machine_id': input_storage.mid}
            sql = sql_cmd_gen.GenSelectSql(conf.TABLE_NAME_SCHEDULE, cols, cond)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)

            if len(res) != 1:
                result_data.status = 400
                raise Exception("bad mid")

            qData = enter_authen.QueryData()
            qData.mid = input_storage.mid
            qData.type = input_storage.type
            qData.code = input_storage.code
            qData.sceneNo = input_storage.sceneNo
            qData.scanType = input_storage.type
            machine_id, qData.cinemaNo, qData.roomNo, qData.dingxinNo, qData.filmCompanyNo = res[0][:5]

            data = {}

            if int(input_storage.type) == enter_authen.SCAN_TYPE_QR_CODE:
                #二维码
                checkFlag, ctcCode = pass_record_check.QrCodeEnterCheck(input_storage.code, input_storage.sceneNo)
                if int(checkFlag) > 0:
                    #是中途离场再返场
                    #pass_record_check.QrCodeReturnAdmit(input_storage.code, input_storage.sceneNo)
                    pass_record_check.CtcCodeReturnAdmit(ctcCode, input_storage.sceneNo)
                    self.__makeWelcomeBackRslt(result_data, ctcCode)
                    printlog('Log', 'll', str(result_data))
                    return self.__returnData(result_data.json())
                qData.code = ctcCode
                qData.reqType = 1

            else:
                #会员卡 蓝牙等
                utype, uid = getUidByScan(input_storage.type, input_storage.code)
                printlog("Debug", "member", "%s,%s" % (utype, uid))
                if (not uid) or (not utype):
                    result_data.status = 400
                    raise Exception(u"无订票信息")

                if uid and uid != '0':
                    checkFlag, ctcCode = pass_record_check.MemberEnterCheck(uid, qData.sceneNo)
                    printlog("Debug", "member", "%s,%s" % (checkFlag, ctcCode))
                    if int(checkFlag) > 0:
                        #中途离场再返场
                        pass_record_check.MemberReturnAdmit(uid, qData.sceneNo)#先减掉权限
                        self.__makeWelcomeBackRslt(result_data, ctcCode)
                        return self.__returnData(result_data.json())

                qData.code = uid
                qData.uid = uid
                if utype == 1:
                    qData.reqType = 3
                elif utype == 2:
                    qData.reqType = 2
                else:
                    result_data.status = 400
                    raise Exception(u"无订票信息")

            #在线鉴权
            self._CheckOnline(qData, data)
            result_data.status = 0
            result_data.substatus = 0
            result_data.message = "success"
            result_data.other_info = ""
            result_data.data = data

        except Exception, e:
            printlog("Error", "Process fail", traceback.format_exc())

            if result_data.status == 0:
                result_data.status = 500
            result_data.substatus = 0
            result_data.message = u"无订票信息"
            result_data.other_info = ""
            result_data.data = {}
            result_data.data['allow_admission_flag'] = 1


        finally :
            end_time = time.time()
            result_data.tcost = int((end_time - beg_time) * 1000000)
            return self.__returnData(result_data.json())


    def _ChangeMsg(self, imsg):
        try:
            MSG_FLAG = u'张票未打印'
            if MSG_FLAG in imsg:
                return u'验票通过,' + imsg[-9:]
            else:
                return imsg
        except:
            return imsg


    def _MockTicketCheck(self, code):
        flag = False
        if code in conf.TICKET_QR_CODE:
            flag = True
        return flag






    def _CheckOnline(self, qData, data):
        data['allow_admission_flag'] = 1 #
        try:
            #-----发起HTTP POST请求-----
            postData = dict(filmCompanyNo = qData.filmCompanyNo,
                            cinemaNo = qData.cinemaNo,
                            hallNo = qData.roomNo,
                            extras = json.dumps({'dingxinHallNo': qData.dingxinNo}),
                            sceneNo = qData.sceneNo,
                            type = qData.reqType,
                            code = qData.code)
            rslt = requests.post(conf.TICKET_CHECK_FORM, postData)
            printlog('Log', 'request', conf.TICKET_CHECK_FORM + str(postData))

            #========构造返回数据===================
            retDict = rslt.json()

            if int(retDict['status']) == 200 or int(retDict['status']) == 0:
                jsonData = retDict['data']
                printlog("Info", "Check return", str(rslt.json()))

                #新入场
                for k in jsonData.keys():
                    data[k] = jsonData[k]
                data['pass_type'] = 1
                if 'lcd_content' in data:
                    data['lcd_content'] = self._ChangeMsg(data['lcd_content'])

                ctcFlag = jsonData['ticket_no']
                if 'ticket_info' in jsonData and \
                   'cinemaTicketCenterFlag' in jsonData['ticket_info'] and\
                   jsonData['ticket_info']['cinemaTicketCenterFlag']:
                    ctcFlag = jsonData['ticket_info']['cinemaTicketCenterFlag']
                data['ctcCode'] = ctcFlag

                #========验证成功，插入入场记录===================
                if  int(jsonData['allow_admission_flag']) == 0:
                    ticketQrMd5 = Md5_32(jsonData['ticket_info']['qrCode'])
                    scanInfoMd5 = Md5_32(qData.code)
                    #是否需要打票
                    if int(jsonData['ticket_info']['ticketStatus']) == 1:
                        data['print_flag'] = 1
                    else:
                        data['print_flag'] = 0

                    printInfo = json.dumps(jsonData['ticket_info'])
                    escPrintInfo = printInfo.replace('\\', '\\\\')

                    sqlData = {
                                'ticket_no': jsonData['ticket_no'],
                                'ticket_qr_code': jsonData['ticket_info']['qrCode'],
                                'ticket_qr_md5':  ticketQrMd5,
                                'scan_type': qData.scanType,
                                'scan_info': qData.code,
                                'scan_info_md5': scanInfoMd5,
                                'scene_no': qData.sceneNo,
                                'cinema_no': qData.cinemaNo,
                                'room_no': qData.roomNo,
                                'ticket_info': escPrintInfo,
                                'is_exit': 0,
                                'ticket_center_flag': ctcFlag,
                                'ff_member_id': qData.uid
                              }
                    sqlCmd = sql_cmd_gen.GenInsertSql(conf.TABLE_NAME_RECORD, sqlData)
                    printlog('Info', 'check online', sqlCmd)
                    res = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)
                    printlog('Info', 'check online', str(res))


                    #在CTC表中记录
                    pass_record_check.CtcNewAdmit(ctcFlag, qData.uid, qData.sceneNo)
                    qData.ticketNo = jsonData['ticket_no']

                    #在鼎新系统中注销
                    self._AdmittanceOnline(qData)
            else:
                data['lcd_content'] = AUTHEN_LCD_CONTENT.get(int(retDict['status']), "")


        except:
            printlog('Error', 'CheckOnline', traceback.format_exc())
            data['allow_admission_flag'] = 1
            #if "message" in retDict:
                #data['lcd_content'] = str(retDict["message"].encode('utf8'))
            #    data['lcd_content'] = retDict["message"]
            return



    def _AdmittanceOnline(self, qData):
        if qData.ticketNo in conf.TICKET_QR_CODE:
            conf.TICKET_QR_CODE.remove(qData.ticketNo)
            sqlCmd = 'update %s set first_enter_time=CURRENT_TIMESTAMP where ticket_no=%s' %\
                     (conf.TABLE_NAME_RECORD, qData.ticketNo)
            res = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)
            return 200, 0, 'ok'

        #========发起HTTP POST请求===================
        postData = dict(filmCompanyNo = qData.filmCompanyNo,
                        cinemaNo = qData.cinemaNo,
                        extras = json.dumps({'dingxinHallNo': qData.dingxinNo}),
                        sceneNo = qData.sceneNo,
                        ticketNo = qData.ticketNo,
                        status = 1)
        rslt = requests.post(conf.TICKET_NOTICE_FORM, postData)
        printlog("Debug", "admittance_notice", conf.TICKET_NOTICE_FORM+str(postData))


