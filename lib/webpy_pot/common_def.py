#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, threading, time, datetime, traceback
import random, urllib2, json

from logger_pot import *


__DEBUG__ = True
__LOG__ = True

class RestfulSender(object):
    """送物品流程
    """
    def __init__(self, timeout=3):
        self.timeout = timeout

    def http_request_get(self, httpReq):
        try:
            sock = urllib2.urlopen(httpReq, timeout=self.timeout)
            ret = json.loads(sock.read())
            return sock.getcode(), ret
        except Exception, e:
            errInfo = traceback.format_exc()
            printlog('Error', 'SendHttp_error', errInfo)
            return 500, None

    def http_request_post(self, httpReq, params):
        try:
            p = urllib2.urlencode(params)
            sock = urllib2.urlopen(httpReq, p, timeout=self.timeout)
            ret = json.loads(sock.read())
            return sock.getcode(), ret
        except Exception, e:
            errInfo = traceback.format_exc()
            printlog('Error', 'SendHttp_error', errInfo)
            return 500, None


class return_data(object) :
    def __init__(self) :
        self.status = 0
        self.substatus = 0
        self.message = ""
        self.other_info = ""
        self.tcost = 0
        self.data = []

    def json(self) :
        inner_dict = {}

        for i in self.__dict__ :
            inner_dict[i] = eval("self." + i)

        return json.dumps(inner_dict)

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.iteritems()]

        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __str__(self):
        return repr(self)

WDLOG.Initialize(server_name='gate_machines', log_path=conf.LOG_PATH,
        log_name='gate_machines', log_level=conf.LOG_LEVEL, log_type=conf.LOG_TYPE)

class MysqlConnPool(object):
    def __init__(self, master, slave):
        self.max_conn = 30
        self.lock = threading._allocate_lock()
        self.curr = 0
        self.conn_list = []

        i = 0
        while i < self.max_conn:
            self.conn_list.append(MysqlClient(master, slave))
            i += 1

    def _getConns(self):
        self.lock.acquire()
        conn = self.conn_list[self.curr]
        self.curr = (self.curr + 1) % self.max_conn
        self.lock.release()

        return conn

    def execute_query(self, db_name, sql, params=None):
        conn = self._getConns()
        rows = conn.execute_query(db_name, sql, params)

        return rows

    def execute_update(self, db_name, sql, params=None):
        conn = self._getConns()
        rows = conn.execute_update(db_name, sql, params)

        return rows

restfulSender = RestfulSender(conf.HTTP_TIMEOUT)
sqlExcutor = MysqlConnPool([conf.MYSQL_INFO], [conf.MYSQL_INFO])

def ParaCheck(paras, *paraSegs):
    for seg in paraSegs:
        if not hasattr(paras, seg):
            return False, 'lost %s in input' % seg
    return True, ''
