#!/usr/bin/python
# -*- coding: utf-8 -*-


def GenSelectSql(tableName, columns, conditions):
    """
        tableName<str>
        columns<list>
        conditions<dict>
    """
    condStr = " and ".join(["%s='%s'" % (k,v) for k,v in conditions.items()])
    colStr = ", ".join(columns)
    return "select %s from %s where %s" % (colStr, tableName, condStr)


def GenInsertSql(tableName, data):
    """
        tableName<str>
        data<dict>
        conditions<dict>
    """
    colStr = ",".join(data.keys())
    valStr = ",".join(["'%s'" %  v for v in data.values()])
    return "insert into %s (%s) value (%s)" % (tableName, colStr, valStr)



def GenUpdateSql(tableName, data, conditions):
    """
        tableName<str>
        data<dict>
        conditions<dict>
    """
    dataStr = ", ".join(["%s='%s'" % (k,v) for k,v in data.items()])
    condStr = " and ".join(["%s='%s'" % (k,v) for k,v in conditions.items()])
    return "update %s set %s where %s" % (tableName, dataStr, condStr)


"""
def SqlSelect(tableName, columns, conditions):
    sqlCmd = GenSelectSql(tableName, columns, conditions)
    return sqlExcutor.execute_query(conf.MYSQL_INFO.get('db_name'), sqlCmd)


def SqlInsert(tableName, data):
    sqlCmd = GenInsertSql(tableName, columns, conditions)
    return sqlExcutor.execute_update(conf.MYSQL_INFO.get('db_name'), sqlCmd)


def SqlUpdate(tableName, data, conditions):
    sqlCmd = GenUpdateSql(tableName, data, conditions)
    return sqlExcutor.execute_update(conf.MYSQL_INFO.get('db_name'), sqlCmd)
"""
