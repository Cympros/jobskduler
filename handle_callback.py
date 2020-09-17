# coding=utf-8
# 最外层的项目配置
import os
import sys

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.insert(0, project_root_path)

from abc import ABCMeta, abstractmethod
from helper import utils_logger


def get_out_dir():
    '临时文件的存放跟目录'
    outer_dir = get_module_root_path() + "/out/"
    if not os.path.exists(outer_dir):
        os.makedirs(outer_dir)
    return outer_dir


def get_module_root_path():
    module_root_dir = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + "/../")
    return module_root_dir


class HandleCallback(metaclass=ABCMeta):

    def read_config(self, task_name, config_key):
        utils_logger.log("HandleCallback.read_config", task_name, config_key)
        if config_key == 'get_project_output_dir':
            return get_out_dir()

    def notify_task_success(self):
        """更新任务状态"""
        pass

    def is_time_support(self, curent_time=None):
        """在curent_time时刻是否允许执行该任务"""
        return True
