# coding=utf-8
# 最外层的项目配置
import os
import re
import sys
import threading

project_root_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.insert(0, project_root_path)

from abc import ABCMeta, abstractmethod
from helper import utils_logger
from helper import utils_android
from helper import utils_common


def get_out_dir():
    """临时文件的存放跟目录"""
    # outer_dir = project_root_path + "/../out/sub.daily-task/"
    outer_dir = os.path.expanduser('~') + "/Downloads/out.sub.daily-task/"
    if not os.path.exists(outer_dir):
        os.makedirs(outer_dir)
    return outer_dir


class HandleCallback(metaclass=ABCMeta):

    def __init__(self):
        pass

    def read_config(self, module, config_key):
        utils_logger.debug("HandleCallback.read_config", module, config_key)
        if config_key == 'get_project_output_dir':
            return get_out_dir()
        elif config_key == "feizu_account":
            return ""
        elif config_key == "feizu_password":
            return ""
        elif config_key == "email_receiver":
            return "firy.itzin@gmail.com"
        elif config_key == "email_sender_host":
            return "smtp.163.com"
        elif config_key == "email_sender_user":
            return "13651968735@163.com"
        elif config_key == "email_sender_pwd":
            return "QPYNHNZLCMBDQIQU"
        elif config_key == "target_device_name":
            # 从线程名中解析deviceName
            thread_name = threading.currentThread().getName()
            utils_logger.debug("thread_name", thread_name)
            tmp_device = None
            if thread_name.startswith("android-thread-"):
                tmp_device = thread_name.strip("android-thread-")
            else:
                connected_devcies = utils_android.get_connected_devcies()
                if connected_devcies is not None and len(connected_devcies) > 0:
                    tmp_device = connected_devcies[0]
            if tmp_device is not None:
                # 若是ip地址,则尝试重连
                compile_rule = re.compile(r'\d+[\.]\d+[\.]\d+[\.]\d+')
                match_list = re.findall(compile_rule, tmp_device)
                if match_list:
                    reconect_res, reconnect_error = utils_common.exec_shell_cmd("adb connect %s" % tmp_device)
                    utils_logger.debug("reconect_res:", reconect_res)
                # 判断设备链接状态
                connected_status, connected_error = utils_common.exec_shell_cmd("adb -s %s get-state" % tmp_device)
                if connected_status != "device" or connected_error is not None:
                    utils_logger.debug("设备断开连接,停止任务")
                    return None
            return tmp_device

    def notify_task_success(self, module_name, task_name):
        """更新任务状态"""
        utils_logger.log("HandleCallback.notify_task_success", module_name, task_name)

    def is_time_support(self, curent_time=None):
        """在curent_time时刻是否允许执行该任务"""
        return True
