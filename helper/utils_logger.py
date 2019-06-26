# coding=utf-8

# 日志管理
import os
import sys
import logging
import threading
from logging.handlers import RotatingFileHandler

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)
import config.env_job

# 普通日志信息，容量受限
logger = logging.getLogger('my_logger')
# 2M的容量
fh = RotatingFileHandler(filename=config.env_job.get_log_file(), maxBytes=5 * 1000 * 1000, backupCount=1)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s-%(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# append日志信息：需要全部申明，若在具体方法中申明会发现存在多个实例会重复打印
append_logger = logging.getLogger("append_logger")
handler = logging.FileHandler(config.env_job.get_append_log_file())
append_logger_formatter = logging.Formatter("%(asctime)s-%(message)s")
handler.setFormatter(append_logger_formatter)
append_logger.addHandler(handler)


def log(*log_infos):
    wrapper_log = ""
    for log_item in log_infos:
        wrapper_log += str(log_item) + " "
        log_preffix = "[" + str(os.getpid()) + ":" + str(threading.currentThread().getName()) + "] "
    logger.warning(log_preffix + wrapper_log)


def append_log(*log_infos):
    wrapper_log = ""
    for log_item in log_infos:
        wrapper_log += str(log_item) + " "
    log(wrapper_log)
    log_preffix = "[" + str(os.getpid()) + ":" + str(threading.currentThread().getName()) + "] "
    append_logger.warning(log_preffix + wrapper_log)
