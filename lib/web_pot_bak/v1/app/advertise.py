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

__MOCK_AD__ = {u'status': 200, u'msg': u'\u6210\u529f', u'data': {u'plans': [{u'startDate': u'2015-01-08 00:00:00', u'endDate': u'2015-02-08 23:59:59', u'target': u'self', u'image': u'h00e9b080aac5bfd11a7f0fda80ebc98163', u'serialName': u'20150108204320', u'urlContent': u'', u'businessName': u'\u901a\u5dde\u9662\u7ebf\u95f8\u673a1\u53f7\u5385\u5e7f\u544a\u56fe\u7247520150111', u'urlSort': u'0', u'position': 1}, {u'startDate': u'2015-01-08 00:00:00', u'endDate': u'2015-01-31 23:59:59', u'target': u'self', u'image': u'h003d599c2606c2168d21e447bdfe770be1', u'serialName': u'20150109105024', u'urlContent': u'', u'businessName': u'\u901a\u5dde\u9662\u7ebf\u95f8\u673a1\u53f7\u5385\u5e7f\u544a\u56fe\u7247420150111', u'urlSort': u'0', u'position': 2},  {u'startDate': u'2015-01-01 00:00:00', u'endDate': u'2015-01-31 23:59:59', u'target': u'self', u'image': u'h0097e94f83846ec3fb552a0696b0ed01ad', u'serialName': u'20150111235211', u'urlContent': u'', u'businessName': u'\u901a\u5dde\u9662\u7ebf\u95f8\u673a1\u53f7\u5385\u5e7f\u544a\u56fe\u724720150111', u'urlSort': u'0', u'position': 3}, {u'startDate': u'2015-01-01 00:00:00', u'endDate': u'2015-01-30 23:59:59', u'target': u'self', u'image': u'h007f2f7e33dc487a7c1718422e0fa76c7c', u'serialName': u'20150111235311', u'urlContent': u'', u'businessName': u'\u901a\u5dde\u9662\u7ebf\u95f8\u673a1\u53f7\u5385\u5e7f\u544a\u56fe\u7247220150111', u'urlSort': u'0', u'position': 4}], u'resourceId': 86, u'plazaId': 1000772, u'number': 4, u'cityId': 110100, u'aliasName': u'8A254D120F099AFAC4DD6A3621F5B28A'}}

class advertise(object) :

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

            checkRslt, msg =  ParaCheck(input_storage, 'mid')
            if not checkRslt:
                result_data.status = 400
                raise Exception("bad params:" + msg)


            sql = 'select alias_name from %s where machine_id="%s"' % (conf.TABLE_NAME_SCHEDULE, input_storage.mid)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
            if len(res) != 1:
                result_data.status = 400
                raise Exception("bad mid")
            aliasName = res[0][0]
            printlog("Debug", "aliasName", aliasName)

            httpPara = {'aliasName' : str(aliasName),
                        'cityId': conf.AD_CITY_ID,
                        'plazaId': conf.AD_PLAZA_ID}
            #rslt = requests.get(conf.ADVERTISE_FORM, params=httpPara, verify=False)
            #paraStr = '&'.join(['%s=%s' % (k,httpPara[k]) for k in httpPara])
            #printlog("Debug", "advertise req", conf.ADVERTISE_FORM + "?" + paraStr)

            #retDict = rslt.json()
            retDict = __MOCK_AD__

            #print log
            if __DEBUG__:
                printlog('Info', 'ad rslt', str(retDict))

            result_data.status = retDict['status']
            result_data.message = retDict['msg']
            if 'data' in retDict:
                result_data.data = retDict['data']
            result_data.other_info = ""

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



    def _ReturnRecord(self, qData, data):
        sqlCmd = 'update %s set is_exit=0 and leave_times=leave_times+1 where ticket_no=%s' % (conf.TABLE_NAME_RECORD, qData.ticketNo)
        res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        retDict = rslt.json()

