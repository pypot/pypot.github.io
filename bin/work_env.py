#coding: utf-8

import os, sys, time, threading, socket


#path
BASE_PATH = '../'
SUB_PATHS = ['conf', 'lib', 'ext', 'src']
sys.path.extend([BASE_PATH + sub_path for sub_path in SUB_PATHS])


#import
import pypot_conf as conf
from logger_pot import *
LOGPOT.Initialize(**conf.LOG_CONF)

