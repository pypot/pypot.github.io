#!/usr/bin/python
# -*- coding: utf-8 -*-


def gen_select_sql(table, columns, conditions):
    """
        table<str>
        columns<list>
        conditions<list>
    """
    cond_str = " and ".join(conditions)
    col_str = ", ".join(columns)
    return "select %s from %s where %s" % (col_str, table, cond_str)


def gen_insert_sql(table, data):
    """
        table<str>
        data<dict>
    """
    col_str = ",".join(data.keys())
    val_str = ",".join(["'%s'" %  v for v in data.values()])
    return "insert into %s (%s) value (%s)" % (table, col_str, val_str)



def gen_update_sql(table, data, conditions):
    """
        table<str>
        data<dict>
        conditions<>
    """
    data_str = ", ".join(["%s='%s'" % (k,v) for k,v in data.items()])
    cond_str = " and ".join(conditions])
    return "update %s set %s where %s" % (table, data_str, cond_str)


