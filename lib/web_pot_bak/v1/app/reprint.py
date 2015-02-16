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


class reprint(object) :
    SCAN_TYPE_BAR_CODE = 1
    SCAN_TYPE_QR_CODE = 2
    SCAN_TYPE_MEMBER_CARD = 3
    SCAN_TYPE_BLUETOOTH =4

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

            checkRslt, msg =  ParaCheck(input_storage, 'mid', 'type', 'code', 'sceneNo')
            if not checkRslt:
                result_data.status = 400
                raise Exception("bad params:" + msg)


            sql = 'select * from %s where machine_id="%s"' % (conf.TABLE_NAME_SCHEDULE, input_storage.mid)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
            if len(res) != 1:
                result_data.status = 400
                raise Exception("bad mid")

            qData = reprint.QueryData()
            qData.mid = input_storage.mid
            qData.machine_id, qData.cinemaNo, qData.roomNo, qData.dingxinNo, qData.filmCompanyNo = res[0][:5]

            data = []
            scanInfoMd5 = Md5_32(input_storage.code)
            if int(input_storage.type) != 2:
                utype, uid = getUidByScan(input_storage.type, input_storage.code)
                scanInfoMd5 = Md5_32(uid)

            sql = 'select ticket_no, ticket_info from %s where scan_info_md5="%s" and scan_type="%s" and scene_no="%s"' % (conf.TABLE_NAME_RECORD, scanInfoMd5, input_storage.type, input_storage.sceneNo)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
            if len(res) < 1:
                result_data.status = 400
                raise Exception("no printing info")
            printlog ('Log', 'res', res)
            for n, i in res:
                data.append({'ticket_no': n, 'ticket_info': json.loads(i)})

            result_data.status = 200
            result_data.message = "success"
            result_data.other_info = ""
            result_data.data = data

            sql = 'update %s set print_times=print_times+1 where scan_info_md5="%s" and scan_type="%s" and scene_no="%s"' % (conf.TABLE_NAME_RECORD, scanInfoMd5, input_storage.type, input_storage.sceneNo)
            res = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sql)

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




