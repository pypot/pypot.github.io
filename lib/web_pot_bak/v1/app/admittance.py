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

__MOCK__ = False
__DEBUG__ = True

class admittance(object) :
    class QueryData(object):
        def __init__(self):
            self.mid = ""
            self.sceneNo = ""
            self.cinemaNo = ""
            self.roomNo = ""
            self.dingxinNo = ""
            self.filmCompanyNo = ""

    def __init__(self) :
        pass

    def __returnData(self, result_data) :
        try :
            self.end_time = time.time()

        except Exception, e:
            exception_info = "Exception(%s), traceback_data(%s)" % (str(e), traceback.format_exc())
            printlog("Error", "Return fail", "%s" % (exception_info))

        finally :
            return result_data + "\n"



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

            checkRslt, msg =  ParaCheck(input_storage, 'mid', 'passType',
                                        'ctcCode', 'enterFlag', 'sceneNo')
            if not checkRslt:
                result_data.status = 400
                raise Exception("bad params:" + msg)


            sql = 'select * from %s where machine_id="%s"' % (conf.TABLE_NAME_SCHEDULE, input_storage.mid)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
            if len(res) != 1:
                result_data.status = 400
                raise Exception("bad mid")

            qData = admittance.QueryData()
            qData.mid = input_storage.mid
            qData.status = str(input_storage.enterFlag)
            qData.ctcCode = input_storage.ctcCode
            qData.machine_id, qData.cinemaNo, qData.roomNo, qData.dingxinNo, qData.filmCompanyNo = res[0][:5]

            data = {}
            result_data.status = 200
            result_data.message = ""
            result_data.other_info = ""
            result_data.data = data

            if int(input_storage.enterFlag) == 2: #未入场
                if pass_record_check.CtcCodeLeave(input_storage.ctcCode,
                                               input_storage.sceneNo) < 0:
                   result_data.status = 400
        except Exception, e:
            exception_info = "In GET() : Exception(%s), traceback_data(%s)" % (str(e), traceback.format_exc())
            printlog("Error", "Process fail", "%s" % (exception_info))

            if result_data.status == 0:
                result_data.status = 500
            result_data.substatus = 0
            result_data.message = str(e)
            result_data.other_info = ""  # str(exception_info)
            result_data.data = {}

        finally :
            end_time = time.time()
            result_data.tcost = int((end_time - beg_time) * 1000000)

            return self.__returnData(result_data.json())



    def _AdmittanceOnline(self, qData, data):
        if int(qData.status) != 1:  #未入场，不调用接口
            return 200, 2004, 'not enter in'
        if qData.ctcCode in conf.TICKET_QR_CODE:
            conf.TICKET_QR_CODE.remove(qData.ctcCode)
            sqlCmd = 'update %s set is_exit=0, first_enter_time=CURRENT_TIMESTAMP where ticket_no=%s' % \
                     (conf.TABLE_NAME_RECORD, qData.ctcCode)
            res = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)
            return 200, 0, 'ok'

        #========发起HTTP POST请求===================
        postData = dict(filmCompanyNo = qData.filmCompanyNo,
                        cinemaNo = qData.cinemaNo,
                        extras = json.dumps({'dingxinHallNo': qData.dingxinNo}),
                        sceneNo = qData.sceneNo,
                        ctcCode = qData.ctcCode,
                        status = qData.status)
        rslt = requests.post(conf.TICKET_NOTICE_FORM, postData)

        #========构造返回数据===================
        if __DEBUG__:
            printlog('Info', 'admittance_return', rslt.json())

        #========验证成功，插入入场记录=========
        retDict = rslt.json()
        status = 200
        substatus = 0
        sqlCmd = 'update %s set is_exit=0, first_enter_time=CURRENT_TIMESTAMP where ticket_no=%s' %  (conf.TABLE_NAME_RECORD, qData.ctcCode)
        res = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)

        #=======获取ticket_no记录的相关信息=========

        #-------插入以取票码为单元的数据------
        ctcFlag, uid = pass_record_check.GetCtcUidByRec(qData.ctcCode)
        if not ctcFlag:
            return status, substatus, retDict['message']

        pass_record_check.CtcNewAdmit(ctcFlag, uid, qData.sceneNo)
        return status, substatus, retDict['message']



    def _ReturnRecord(self, qData, data):
        #sqlCmd = 'update %s set is_exit=0, leave_times=leave_times+1 where ticket_no=%s' % (conf.TABLE_NAME_RECORD, qData.ctcCode)
        #res = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        #if res != 1:
        #    data['message'] = 'update admittance info error'
        #    return False
        #return True
        ctcFlag, uid = pass_record_check.GetCtcUidByRec(qData.ctcCode)
        if not ctcFlag:
            return status, substatus, retDict['message']
        if not uid:
            uid = ''
        if pass_record_check.CtcAdmit(ctcFlag, uid, qData.sceneNo) < 0:
            return False
        return True

