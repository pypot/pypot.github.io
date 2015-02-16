#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, threading, time, datetime, traceback
import random, urllib2, json

import web
from common_def import *
from encrypt import *
import requests
import server_conf as conf

__MOCK__ = False
__DEBUG__ = True

class set_room_info(object) :

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

            checkRslt, msg =  ParaCheck(input_storage, 'mid', 'roomNo')
            if not checkRslt:
                result_data.status = 400
                raise Exception("bad params:" + msg)


            sql = 'select * from %s where machine_id="%s"' % (conf.TABLE_NAME_SCHEDULE, input_storage.mid)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
            if len(res) != 1:
                result_data.status = 400
                raise Exception("bad mid")

            sqlCmd = 'update %s set room_no="%s", dingxin_no="%s" where machine_id="%s"' % (
                      conf.TABLE_NAME_SCHEDULE, input_storage['roomNo'], input_storage['roomNo'], input_storage['mid'])
            res = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)
            if res < 1:
                result_data.message = u"没有更换影厅"
            result_data.other_info = ""
            result_data.data = {}

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



