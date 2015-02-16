#coding: utf8

# [Basic Info]
WORK_HOME = "/home/yangfan51/develop/dssvn/trunk/intelligentservice/pypot/"

LOG_CONF = dict( 
                server_name = 'pypot_test',
                log_path = WORK_HOME + 'log/',
                log_name='pypot_test',
                log_type = 1,
                log_level = 'feild'
               )
                
        

HTTP_TIMEOUT = 3000  # ms
WAITING_TIME = 15  # minute
CHECKING_TIME = 10  # minute

# [Film Links]
FILM_LINK_FORM = "http://piao.test.wanhui.cn/web/films/scenes?"
TICKET_CHECK_FORM = "http://piao.test.wanhui.cn/web/films/gate/check"
TICKET_NOTICE_FORM = "http://piao.test.wanhui.cn/web/films/gate/admittance"


FETCH_QR_CODE = {"43317197914035" : 1}

TICKET_QR_CODE = set(['12130000001',
                      '12130000002',
                      '12130000003',
                      '12130000004',
                      '12130000005'])


# [ Mysql Info ]
MYSQL_INFO = {
                 "host" : "10.77.135.214",
                 "port" : 3316,
                 "user" : "search",
                 "passwd" : "search",
                 "db_name" : "test"
             }

TABLE_NAME_SCHEDULE = "gate_machine_resource"
TABLE_NAME_WORKER = "gate_worker_authen"
TABLE_NAME_RECORD = "gate_pass_recorder"
TABLE_NAME_PRIVILEGE = "gate_privilege"
TABLE_NAME_CTCFALG = "gate_pass_ctcflag_recorder"

CINEMA_MEMBER = {
        #"E0633804" : "94141414141414",
        "E0633804" : "15000000000000594",
        #"8BFCFFEF" : "94141414141414"
        "8BFCFFEF" : "15000000000000594",
        "3B1AB089" : "15000000000000594",
        "AB28AF89" : "15000000000000594",
        "" : "15000000000000083"
        }




#############飞凡卡配置信息############
FF_MEMBER_LOGIN_URL = "https://api.wanhui.cn/ucenter/v2/users"
LOGIN_TYPE_CARD = 7

FF_MEMBER = {
        #"8888200021819938" : "94141414141414"
        "8888200021819938" : "3012345678901234",
        "1012345678901234" : "15000000000000594"
        }


#############广告配置信息############
ADVERTISE_FORM = "https://sandbox.api.wanhui.cn/advertise/v1/materials"
AD_CITY_ID = 110100
AD_PLAZA_ID = 1000772
