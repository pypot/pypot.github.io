# coding: utf-8
# Logger Class Lib.
# author: phanyoung@pypot.com
# date: 2015/05/21
# version: 1.0

import os, sys, time, threading, socket
import logging
import logging.handlers



class Singleton(object):
    __lock = threading.Lock()

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            Singleton.__lock.acquire()
            if not hasattr(cls, '_instance'):
                org = super(Singleton, cls)
                cls._instance = org.__new__(cls)
            Singleton.__lock.release()
        return cls._instance



class LoggerPot(Singleton):
    LEVEL_NONE  = 0x00
    LEVEL_INFO  = 0x01
    LEVEL_LOG   = 0x02
    LEVEL_DEBUG = 0x04
    LEVEL_ERROR = 0x08
    LEVEL_FATAL = 0x10
    LEVEL_ALL = 0xFFFFFFFF
    __logging = None
    LOGING_MAP = {LEVEL_INFO: lambda x : Singleton.__logging.info(x),
                  LEVEL_LOG:  lambda x : Singleton.__logging.info(x),
                  LEVEL_DEBUG: lambda x : Singleton.__logging.debug(x),
                  LEVEL_ERROR: lambda x : Singleton.__logging.error(x),
                  LEVEL_FATAL: lambda x : Singleton.__logging.fatal(x)
                 }

    def Initialize(self, server_name="testlog", log_id="001", log_path="./", log_name="log", log_interval=1, log_time_unit='H',
                   log_format="[%(asctime)s][%(levelname)s] %(message)s",
                   log_suffix="%Y%m%d_%H%M.log", log_level="efil", log_type="1", scribe_ip="127.0.0.1", scribe_port=1464):
        self.__server_map = {LoggerPot.LEVEL_LOG   : server_name + "_l",
                             LoggerPot.LEVEL_ERROR : server_name + "_e",
                             LoggerPot.LEVEL_FATAL : server_name + "_f"}
        Singleton.__logging = self.__init_logger(log_id, log_path, log_name, log_interval,
                                               log_time_unit, log_format, log_suffix, log_level)

        self.__scribe_ip = scribe_ip
        self.__scribe_port = scribe_port
        self.__log_type = log_type
        self.__host = socket.gethostname()# 获取hostname

        if len(log_level) > 0:
            self.__level = 0
            if log_level.find('f') >= 0:
                self.__level |= LoggerPot.LEVEL_FATAL
                Singleton.__logging.setLevel(logging.CRITICAL)
            if log_level.find('e') >= 0:
                self.__level |= LoggerPot.LEVEL_ERROR
                Singleton.__logging.setLevel(logging.ERROR)
            if log_level.find('i') >= 0:
                self.__level |= LoggerPot.LEVEL_INFO
                Singleton.__logging.setLevel(logging.INFO)
            if log_level.find('l') >= 0:
                self.__level |= LoggerPot.LEVEL_LOG
                Singleton.__logging.setLevel(logging.INFO)
            if log_level.find('d') >= 0:
                self.__level |= LoggerPot.LEVEL_DEBUG
                Singleton.__logging.setLevel(logging.DEBUG)
        else:
            self.__level = LoggerPot.LEVEL_INFO | LoggerPot.LEVEL_ERROR | LoggerPot.LEVEL_FATAL | LoggerPot.LEVEL_LOG
            logging.basicConfig(level=logging.INFO)


    # 输出Info日志
    def Info(self, kv):
        if self.IsLog(LoggerPot.LEVEL_INFO):
            f = sys._getframe().f_back
            if f is not None:
                f = f.f_back

            msg = self.LogHeader(f.f_code.co_filename, f.f_lineno)
            for item in kv:
              if len(item) == 2:
                v = str(item[1]).replace("%3A", "%%3A")
                v = v.replace(";", "%3A")
                msg = "%s;%s=%s" % (msg, item[0], v)
            self.__log(LoggerPot.LEVEL_INFO, msg)


    # 输出Debuf日志
    def Debug(self, kv):
        if self.IsLog(LoggerPot.LEVEL_DEBUG):
            f = sys._getframe().f_back
            if f is not None:
                f = f.f_back

            msg = self.LogHeader(f.f_code.co_filename, f.f_lineno)
            for item in kv:
              if len(item) == 2:
                v = str(item[1]).replace("%3A", "%%3A")
                v = v.replace(";", "%3A")
                msg = "%s;%s=%s" % (msg, item[0], v)
            self.__log(LoggerPot.LEVEL_DEBUG, msg)

    # 输出Log日志
    def Log(self, kv):
        if self.IsLog(LoggerPot.LEVEL_LOG):
            f = sys._getframe().f_back
            if f is not None:
                f = f.f_back

            msg = self.LogHeader(f.f_code.co_filename, f.f_lineno)
            for item in kv:
              if len(item) == 2:
                v = str(item[1]).replace("%3A", "%%3A")
                v = v.replace(";", "%3A")
                msg = "%s;%s=%s" % (msg, item[0], v)
            self.__log(LoggerPot.LEVEL_LOG, msg)

    # 输出Erorr日志
    def Error(self, kv):
        if self.IsLog(LoggerPot.LEVEL_ERROR):
            f = sys._getframe().f_back
            if f is not None:
                f = f.f_back

            msg = self.LogHeader(f.f_code.co_filename, f.f_lineno)
            for item in kv:
              if len(item) == 2:
                v = str(item[1]).replace("%3A", "%%3A")
                v = v.replace(";", "%3A")
                msg = "%s;%s=%s" % (msg, item[0], v)
            self.__log(LoggerPot.LEVEL_ERROR, msg)

    # 输出Fatal日志
    def Fatal(self, kv):
        if self.IsLog(LoggerPot.LEVEL_FATAL):
            f = sys._getframe().f_back
            if f is not None:
                f = f.f_back

            msg = self.LogHeader(f.f_code.co_filename, f.f_lineno)
            for item in kv:
              if len(item) == 2:
                v = str(item[1]).replace("%3A", "%%3A")
                v = v.replace(";", "%3A")
                msg = "%s;%s=%s" % (msg, item[0], v)
            self.__log(LoggerPot.LEVEL_FATAL, msg)

    # 设置LogLevel
    def EnableLog(self, level):
        self.__level |= level

    def DisableLog(self, level):
        self.__level &= ~level

    def IsLog(self, level):
        return (self.__level & level) != 0

    def SetLevel(self, level):
        self.__level = level

    def GetLevel(self):
        return self.__level

    # 获取日志头
    def LogHeader(self, f=None, line=0):
        if f and f.rfind("/") > 0:
          f = f[f.rfind("/") + 1:]
        if f:
            return "[%s:%u] " % (f, line)
        else:
            return ""

    def __init_logger(self, log_id, log_path, log_name, log_interval, log_time_unit,
                    log_format, log_suffix, log_level):
        """ 初始化logger """
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        log_file = os.path.join(log_path, log_name)
        handler = logging.handlers.TimedRotatingFileHandler(\
            log_file, log_time_unit, log_interval, 240)
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        handler.suffix = log_suffix
        logger = logging.getLogger()
        logger.addHandler(handler)
        return logger

    def init_multiprocess_logger(log_id, log_path, log_name, log_interval, log_time_unit,
                    log_format, log_suffix, log_level):
        """ 初始化支持多进程的logger """
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        log_file = os.path.join(log_path, log_name)
        handler = MultiProcessLogHandler(\
            log_file, log_time_unit, log_interval, 240)
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        handler.suffix = log_suffix
        # logger = logging.getLogger(log_id)
        logger = logging.getLogger()
        logger.addHandler(handler)
        # logger.setLevel(log_level)

        return logger

    # 打印日志
    def __log(self, level, msg):
        LoggerPot.LOGING_MAP[level](msg)

class MultiProcessLogHandler(logging.Handler):
    def __init__(self, log_file, log_time_span, log_interval, backup_cnt=0):
        """ 初始化
        # parameters:
        #   log_file: 日志名称
        #   log_time_span: 日志切分粒度('H'-hours, 'M'-minutes, 'midnight'-at midnight）
        #   log_interval: 日志间隔
        #   backup_cnt: 非0表示最多纪录多少份日志，然后除旧迎新
        """
        logging.Handler.__init__(self)
        self._handler = TimedRotatingFileHandler(log_file, log_time_span, log_interval, backup_cnt)
        self.queue = multiprocessing.Queue(-1)
        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    def setSuffix(self, suffix):
        self._handler.suffix = suffix

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args
        # have been stringified.  Removes any chance of
        # unpickleable things inside and possibly reduces
        # message size sent over the pipe
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            dummy = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self._handler.close()
        logging.Handler.close(self)




LOGPOT = LoggerPot()
#LOGPOT = None

def printlog(level, strKey, strVal):
    if LOGPOT:
        getattr(LOGPOT, level)([(strKey, strVal)])
    else:
        print "%s: %s=%s" % (level, strKey, strVal)


