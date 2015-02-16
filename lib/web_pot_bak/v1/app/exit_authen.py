#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, threading, time, datetime, traceback
import random, urllib2, json

import web
from common_def import *
from encrypt import *

import server_conf as conf
import pass_record_check

class exit_authen(object) :
    def __init__(self) :
        pass

    def __returnData(self, result_data) :
        try :
            self.end_time = time.time()

        except Exception, e:
            exception_info = "Exception(%s), traceback_data(%s)" % (str(e), traceback.format_exc())
            printlog("Error", "Return fail", "%s" % (exception_info))

        finally :
            printlog("Debug", "exit authen return", str(result_data))
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
            # printlog("Log", "GET Params ok", "input_ctx_dict : %s" % (str(input_ctx_dict)))

            mid = str(input_storage.get("mid", ""))
            code = str(input_storage.get("code", ""))
            scanType = int(input_storage.get("type", 0))
            sceneNo = str(input_storage.get("sceneNo", ""))

            if len(mid) <= 0 or len(code) <= 0 or len(sceneNo) <= 0 or scanType ==0:
                result_data.status = 400
                raise Exception("bad params")

            sql = "select * from %s where machine_id=\"%s\"" % (conf.TABLE_NAME_SCHEDULE, mid)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
            if len(res) != 1:
                result_data.status = 400
                raise Exception("bad mid")

            data = {}
            data["allow_admission_flag"] = 1
            data["cinema_name"] = ""

            if scanType == 2:
                #二维码
                checkFlag, ctcCode = pass_record_check.QrCodeExitCheck(input_storage.code,
                                                                       input_storage.sceneNo)
                data["pass_type"] = 2
                data["ctcCode"] = ctcCode
                if checkFlag > 0:
                    data["allow_admission_flag"] = 0


            else:
                #其它会员介质
                utype, uid = getUidByScan(input_storage.type, input_storage.code)
                if (not uid) or (not utype):
                    result_data.status = 400
                    raise Exception(u"无订票信息")

                if uid and uid != '0':
                    checkFlag, ctcCode = pass_record_check.MemberExitCheck(uid, input_storage.sceneNo)
                    data["pass_type"] = 1
                    data["ctcCode"] = ctcCode
                    data["cinema_name"] = ""
                    data["ticket_no"] = ""

                    if checkFlag > 0:
                        data["allow_admission_flag"] = 0

            result_data.status = 0
            result_data.substatus = 0
            result_data.message = "success"
            result_data.other_info = ""
            result_data.data = data

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

