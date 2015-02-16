#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, threading, time, datetime, traceback
import random, urllib2, json

import web
from common_def import *
from encrypt import *
import requests
import server_conf as conf
from sql_cmd_gen import *
import traceback

__MOCK__ = False


class WebFrame(object) :
    key_paras = []

    def __return_data(self, result_data) :
        try :
            self.end_time = time.time()

        except Exception, e:
            exception_info = "Exception(%s), traceback_data(%s)" % (str(e), traceback.format_exc())
            printlog("Error", "Return fail", "%s" % (exception_info))

        finally :
            return result_data + "\n"

    def get_core_func(self, input_storage, result_data):
        pass

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

            checkRslt, msg =  ParaCheck(input_storage, **self.__class__.key_paras) 
            if not checkRslt:
                result_data.status = 400
                raise Exception("bad params:" + msg)

            #验证mid合法性
            sql = 'select * from %s where machine_id="%s"' % (conf.TABLE_NAME_SCHEDULE, input_storage.mid)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)

            if len(res) != 1:
                result_data.status = 400
                raise Exception("bad mid")

            #执行功能
            self.get_core_func(input_storage, result_data)

        except Exception, e:
            printlog("Error", "Process fail", "%s" % (traceback.format_exc()))

            if result_data.status == 0:
                result_data.status = 500
            result_data.substatus = 0
            result_data.message = str(e)
            result_data.other_info = ""  # str(exception_info)
            result_data.data = {}

        finally :
            end_time = time.time()
            result_data.tcost = int((end_time - beg_time) * 1000000)

            return self.__return_data(result_data.json())




