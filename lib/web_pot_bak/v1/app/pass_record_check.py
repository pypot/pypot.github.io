#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, threading, time, datetime, traceback
import random, urllib2, json
from functools import partial

import web
from common_def import *
from encrypt import *
import requests
import server_conf as conf


CTC_TABLE = conf.TABLE_NAME_CTCFALG
TICKET_TABLE = conf.TABLE_NAME_RECORD

#==============基础函数===================


def GetCtcUidByRec(ticketNo):
    sqlCmd = 'select ticket_center_flag, ff_member_id from %s where ticket_no=%s' % \
            (TICKET_TABLE, ticketNo)
    res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sqlCmd)
    if len(res) < 1:
        return None, None
    return res[0][:2]


def GetValidCtcFlag(uid, sceneNo):
    '''获取uid下的一个还能返场的取票码
    一个uid下可能有多个取票码
    '''
    try:
        #注意uid不能为'0'、0、空
        sqlCmd = 'select ticket_center_flag from %s where ff_member_id=%s and scene_no="%s" and inside_count < enter_count' % (CTC_TABLE, uid, sceneNo)
        res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        if len(res) < 1:
            return None
        #一个会员可能有多个取票码
        return res[0][0]

    except:
        return None


def GetCtcFlagByQrCode(qrCode, sceneNo):
    try:
        #is ticket qr code?
        qrMd5 = Md5_32(qrCode)
        sqlCmd = 'select ticket_center_flag from %s where ticket_qr_md5="%s" and scene_no="%s"' % (TICKET_TABLE, qrMd5, sceneNo)
        res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        if len(res) >= 1 and (res[0][0]):
            return res[0][0]
        else:
            return qrCode
    except:
        printlog("Error", "", traceback.format_exc())
        return None



def IsValidUid(uid):
    '''判断一个uid是否是有效的
    '''
    return (uid and int(uid) != 0)



#==============首次入场通知===================

def CtcNewAdmit(ctcCode, uid, sceneNo):
    try:
        if IsValidUid(uid):
            #开始刷的取票码，没有会员ID信息，则在此时加上ID信息
            sqlCmd = 'update %s set enter_count=enter_count+1, inside_count=inside_count+1, ff_member_id="%s" where ticket_center_flag="%s" and scene_no="%s"' % (CTC_TABLE, uid, ctcCode, sceneNo)
        else:
            sqlCmd = 'update %s set enter_count=enter_count+1, inside_count=inside_count+1 where ticket_center_flag="%s" and scene_no="%s"' % (CTC_TABLE, ctcCode, sceneNo)

        rnum = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)

        if rnum < 1:
            sqlCmd = 'insert into %s (ticket_center_flag, enter_count, inside_count, ff_member_id, scene_no) value ("%s", 1, 1, "%s", "%s")' % (conf.TABLE_NAME_CTCFALG, ctcCode, uid, sceneNo)
            rnum = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)
            if rnum < 1:
                raise Exception("some err")
        return 0

    except:
        return -2



#===========返场鉴权===================

def MemberEnterCheck(uid, sceneNo):
    '''返场鉴权，使用会员号
    返回值
        -1 -- 不能入场
        0 -- 没有记录
        1 -- 可以入场
    '''
    try:
        ctcCode = GetValidCtcFlag(uid, sceneNo)
        if ctcCode:
            return 1, ctcCode
        return 0, ''
    except:
        return -2, ''


def QrCodeEnterCheck(qrCode, sceneNo):
    '''返场鉴权，使用二维码
    返回值小于等于0时，要在线鉴权
    '''
    try:
        ctcCode = GetCtcFlagByQrCode(qrCode, sceneNo)
        sqlCmd = 'select enter_count, inside_count from %s where ticket_center_flag="%s" and scene_no="%s"' % (CTC_TABLE, ctcCode, sceneNo)
        res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        if len(res) < 1:
            return 0, qrCode

        enterCnt, insideCnt = res[0][:2]
        printlog("Log", ctcCode, "%s,%s" % (enterCnt, insideCnt)) 
        if int(insideCnt) < int(enterCnt):
            return 1, ctcCode
        else:
            return -1, ctcCode
    except:
        printlog("Error", "", traceback.format_exc())
        return -2, qrCode




#===========返场通知===================

def BaseReturnAdmit(codeTransFunc, oriCode, sceneNo):
    ''' 中途返场，用二维码
    '''
    try:
        ctcCode = codeTransFunc(oriCode, sceneNo)
        if not ctcCode:
            raise Exception("some err")
        sqlCmd = 'update %s set inside_count=inside_count+1, leave_times=leave_times+1 where ticket_center_flag="%s" and scene_no="%s"' % (CTC_TABLE, ctcCode, sceneNo)
        printlog("Debug", "ReturnAdmit", sqlCmd)
        rnum = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        if rnum < 1:
            raise Exception("some err")
        return 0
    except:
        printlog("Debug", "BaseReturnAdmit", traceback.format_exc())
        return -2


CtcCodeReturnAdmit = partial(BaseReturnAdmit, lambda c,s: c)
QrCodeReturnAdmit = partial(BaseReturnAdmit, GetCtcFlagByQrCode)
MemberReturnAdmit = partial(BaseReturnAdmit, GetValidCtcFlag)






#===========出场鉴权===================
def QrCodeExitCheck(qrCode, sceneNo):
    ''' 中途返场，用二维码
    '''
    try:
        ctcCode = GetCtcFlagByQrCode(qrCode, sceneNo)
        #sqlCmd = 'select ticket_center_flag from %s where ticket_center_flag="%s" and scene_no="%s"' % (CTC_TABLE, ctcCode, sceneNo)
        sqlCmd = 'select ticket_center_flag from %s where ticket_center_flag="%s" and scene_no="%s" and inside_count>0' % (CTC_TABLE, ctcCode, sceneNo)
        res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        if len(res) < 1:
            return 0, ''
        else:
            return 1, ctcCode
    except:
        return -2, ''



def MemberExitCheck(uid, sceneNo):
    ''' 使用会员身份出场鉴权
    只要有记录，就让出场.
    '''
    try:
        sqlCmd = 'select ticket_center_flag, enter_count, inside_count from %s where ff_member_id=%s and scene_no="%s" and inside_count>0' % (CTC_TABLE, uid, sceneNo)
        res = sqlExcutor.execute_query(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        if len(res) < 1:
            return 0, ''
        #一个会员可能有多个取票码
        ctcCode = res[0][0]
        if not ctcCode:
            return 0, ''
        return 1, ctcCode
    except:
        return -2, ''





#===========出场通知===================


def BaseLeave(codeTransFunc, oriCode, sceneNo):
    try:
        ctcCode = codeTransFunc(oriCode, sceneNo)
        if not ctcCode:
            printlog("Error", "BaseLeave:CTCCode", str(ctcCode))
            raise Exception("some err")

        sqlCmd = 'update %s set inside_count=inside_count-1 where ticket_center_flag="%s" and scene_no="%s"' % (CTC_TABLE, ctcCode, sceneNo)
        rnum = sqlExcutor.execute_update(conf.MYSQL_INFO.get("db_name"), sqlCmd)
        if rnum < 1:
            printlog("Error", "BaseLeave:SQL", str(sqlCmd))
            raise Exception("some err")
        return 0

    except:

        printlog("Error", "BaseLeave:SQL", str(traceback.format_exc()))
        return -2


CtcCodeLeave = partial(BaseLeave, lambda c,s: c)
MemberLeave = partial(BaseLeave, GetValidCtcFlag)
QrCodeLeave = partial(BaseLeave, GetCtcFlagByQrCode)

