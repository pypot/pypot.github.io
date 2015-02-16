#!/usr/bin/python
# -*- coding: utf-8 -*-

from include import *
from common_def import *
from web_frame import *
import pass_record_check
import server_conf as conf


class Leave(WebFrame):

    def get_core_func(self, input_storage, result_data):
        pass

class leave(object) :
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
            # printlog("Log", "GET Params ok", "input_ctx_dict : %s" % (str(input_ctx_dict)))

            mid = str(input_storage.get("mid", ""))
            ctcCode = str(input_storage.get("ctcCode", ""))
            exitFlag = int(input_storage.get("exitFlag", 0))
            sceneNo = str(input_storage.get("sceneNo", ""))

            if len(mid) <= 0 or len(ctcCode) <= 0 or len(sceneNo) <= 0 :
                result_data.status = 400
                raise Exception("bad params")
            if exitFlag != 1 and exitFlag != 2:
                result_data.status = 400
                raise Exception("bad exitFlag")

            #sql = "select * from %s where machine_id=\"%s\"" % (conf.TABLE_NAME_SCHEDULE, mid)
            #res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
            #if len(res) != 1:
            #    result_data.status = 400
            #    raise Exception("bad mid")

            if exitFlag == 1:
                #加上入场权限
                pass_record_check.CtcCodeLeave(ctcCode, sceneNo)

            result_data.status = 0
            result_data.substatus = 0
            result_data.message = "success"
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
