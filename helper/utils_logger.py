# coding=utf-8

# 日志管理
import os
import sys
import logging
import threading
from logging.handlers import RotatingFileHandler

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)


def get_log_file():
    return os.path.abspath(root_path + '/out/logger.log.txt')


# 普通日志信息，容量受限
logger = logging.getLogger('my_logger')
# 2M的容量
fh = RotatingFileHandler(filename=get_log_file(), maxBytes=5 * 1000 * 1000, backupCount=1)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s-%(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


def log(*log_infos):
    wrapper_log = ""
    for log_item in log_infos:
        wrapper_log += str(log_item) + " "
        log_preffix = "[" + str(os.getpid()) + ":" + str(threading.currentThread().getName()) + "] "
    logger.warning(log_preffix + wrapper_log)
