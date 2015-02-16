#!/usr/bin/python
# -*- coding: utf-8 -*-

from include import *
import os, threading, time, datetime, traceback
import random, urllib2, json
import datetime

import web
import sys

from common_def import *

import server_conf as conf

#__MOCK_SCHEDULE__ = {u'status': 0, u'other_info': u'', u'substatus': 0, u'message': u'success', u'data': {u'scene_list': [{u'cinemaNo': u'992', u'canUsePoint': 0, u'cityNo': u'320100', u'leavingTime': 1421334420000, u'cinemaTitle': u'\u5357\u4eac\u65b0\u8857\u53e3\u4e07\u8fbe\u5e7f\u573a\u5e97', u'checkingTime': 1421321100000, u'saleEndTime': 1421305256000, u'saleStartTime': 1421305256000, u'availableNum': 239, u'status': 1, u'showEndTime': 1421335020000, u'filmTitle': u'\u4e00\u751f\u6709\u4f60', u'showStartDate': 1421321700000, u'price': u'80.00', u'storeId': 9051049, u'showEndDate': 1421335020000, u'mainPosterPic': u'h0004fff640a53c9607148adaf5ee41c64d', u'dimen': u'IMAX2D', u'screeningRoomNo': u'2', u'language': u'\u56fd\u8bed', u'filmNo': u'1416218307118', u'sceneNo': u'20150113101510289009', u'showStartTime': 1421321700000, u'waitingTime': 1421320800000, u'filmCompanyNo': u'wandacinemas', u'lastTime': u'222', u'totalNum': 248}], u'room_no': u'2'}, u'tcost': 20914}


__MOCK_CUR_TIME__ = 1423230100

__MOCK_FLAG__ = True

def TimeChange(stmp):
    return datetime.datetime.fromtimestamp(stmp / 1000).strftime("%Y-%m-%d %H:%M:%S")


class schedule(object) :
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
        #return json.dumps(__MOCK_SCHEDULE__)

        try :
            input_storage = web.input()
            input_post_str = web.data()
            input_ctx_dict = web.ctx

            printlog("Log", "GET Params ok", "inner_url : %s" % (str(inner_url)))
            printlog("Log", "GET Params ok", "input_storage : %s" % (str(input_storage)))
            printlog("Log", "GET Params ok", "input_post_str : %s" % (str(input_post_str)))
            # printlog("Log", "GET Params ok", "input_ctx_dict : %s" % (str(input_ctx_dict)))

            mid = str(input_storage.get("mid", ""))
            period = int(input_storage.get("period", "1"))

            if len(mid) <= 0 or period < 0 or period > 2:
                result_data.status = 400
                raise Exception("bad params")

            sql = "select machine_id, cinema_no, room_no, dingxin_no, film_campany_no from %s where machine_id=\"%s\"" % (conf.TABLE_NAME_SCHEDULE, mid)
            res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
            if len(res) != 1:
                result_data.status = 400
                raise Exception("bad mid")

            (machine_id, cinema_no, room_no, dingxin_no, film_campany_no) = res[0][:5]

            url = "%s" % (conf.FILM_LINK_FORM)
            if len(cinema_no) > 0:
                url = url + "%s=%s" % ("cinemaNo", cinema_no)
            if len(room_no) > 0:
                url = url + "&%s=%s" % ("screeningRoomNo", room_no)

            scenes = []
            retcode, data = restfulSender.http_request_get(url)
            if retcode == 0 or retcode == 200:
                if data.has_key("data") and data["data"].has_key("filmScenes"):
                    scenes = data["data"]["filmScenes"]
                else:
                    result_data.status = 500
                    raise Exception("get wrong film data")
            else:
                result_data.status = 500
                raise Exception("failed to get film data")

            data = []
            curr_time = int(time.time())
            for scene in scenes:
                showStartTime = int(scene["showStartTime"]) / 1000
                showEndTime = int(scene["showEndTime"]) / 1000
                waitingTime = showStartTime - conf.WAITING_TIME * 60
                checkingTime = showStartTime - conf.CHECKING_TIME * 60
                leavingTime = showEndTime - conf.CHECKING_TIME * 60

                scene["waitingTime"] = waitingTime * 1000
                scene["checkingTime"] = checkingTime * 1000
                scene["leavingTime"] = leavingTime * 1000

                if period == 0:  # 获取当天
                    if showStartTime / 86400 == curr_time / 86400:
                       data.append(scene)
                elif period == 1:
                    if __MOCK_FLAG__:
                        curr_time = __MOCK_CUR_TIME__
                    if curr_time >= waitingTime and curr_time <= leavingTime:
                        data.append(scene)
                elif period == 2:
                    if curr_time < waitingTime:
                        if len(data) <= 0:
                            data.append(scene)
                        else:
                            showStartTime1 = int(data[0]["showStartTime"]) / 1000
                            if showStartTime < showStartTime1:
                                data[0] = scene
                else:
                    pass

            pak = {}
            pak["room_no"] = str(room_no)
            pak["scene_list"] = data

            result_data.status = 0
            result_data.substatus = 0
            result_data.message = "success"
            result_data.other_info = ""
            result_data.data = pak

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

