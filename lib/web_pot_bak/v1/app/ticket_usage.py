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
from web_frame import *



class TicketUsage(WebFrame):
    key_paras = ["mid", "ctcCode", "sceneNo"]


    def get_core_func(self, input_storage, result_data):
        #查询ctcCode进出场信息
        columns = ['enter_count', 'inside_count']
        conditions = {'ticket_center_flag': input_storage.ctcCode,
                      'scene_no': input_storage.sceneNo
                     }
        sql = GenSelectSql(conf.TABLE_NAME_CTCFALG, columns, conditions)
        res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sql)
        if len(res) < 1:
            result_data.status = 400
            raise Exception("no usage info")
        printlog ('Debug', 'ctccode_info : %s' % input_storage.ctcCode, res)
        enterCnt = int(res[0][0])
        insideCnt = int(res[0][1])
        outsideCnt = enterCnt - insideCnt
        data = {"enterCnt": enterCnt,
                "insideCnt": insideCnt,
                "outsideCnt": outsideCnt
               }
        result_data.status = 200
        result_data.message = "success"
        result_data.other_info = ""
        result_data.data = data

