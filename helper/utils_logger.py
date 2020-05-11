# coding=utf-8

# 日志管理
import os
import sys
import json
import logging
import threading
import inspect
from logging.handlers import RotatingFileHandler

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.insert(0, project_root_path)


def get_log_file():
    log_dir = project_root_path + "/out"
    if os.path.exists(log_dir) is False:
        os.makedirs(log_dir)
    return os.path.abspath(log_dir + "/logger_" + str(threading.currentThread().getName()) + ".txt")


# 普通日志信息，容量受限
logger = logging.getLogger('my_logger')
# 2M的容量
formatter = logging.Formatter("%(asctime)s%(message)s")

fh = RotatingFileHandler(filename=get_log_file(), maxBytes=5 * 1000 * 1000, backupCount=1)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def log(*log_infos):
    inspect_stack = inspect.stack()
    module_path = inspect_stack[1][1]
    module=os.path.splitext(os.path.basename(module_path))[0]
    method_name = inspect_stack[1][3]  # 所在方法名
    wrapper_log = ""
    for log_item in log_infos:
        wrapper_log += str(log_item) + " "
        log_preffix = "[" + str(os.getpid()) + "]<" + str(module) + "#" + str(method_name) + ">         "
    logger.warning(log_preffix + wrapper_log)
