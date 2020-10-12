# coding=utf-8
# 最外层的项目配置
import os
import sys

project_root_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.insert(0, project_root_path)

from abc import ABCMeta, abstractmethod
from helper import utils_logger


def get_out_dir():
    """临时文件的存放跟目录"""
    outer_dir = project_root_path + "/../out/sub.daily-task/"
    if not os.path.exists(outer_dir):
        os.makedirs(outer_dir)
    return outer_dir


class HandleCallback(metaclass=ABCMeta):

    def __init__(self):
        pass

    def read_config(self, module_name, task_name, config_key):
        utils_logger.debug("HandleCallback.read_config", module_name, task_name, config_key)
        if config_key == 'get_project_output_dir':
            return get_out_dir()

    def notify_task_success(self, module_name, task_name):
        """更新任务状态"""
        utils_logger.log("HandleCallback.notify_task_success", module_name, task_name)

    def is_time_support(self, curent_time=None):
        """在curent_time时刻是否允许执行该任务"""
        return True
