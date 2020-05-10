# coding=utf-8

import json
import os
import sys
import threading

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(project_root_path)

from helper import utils_logger
from helper import utils_common
from helper import envs


class BaseTask():
    def __init__(self):
        self.upload_files = []  # 用于存储待上传的文件列表
        self.task_session = None

    def is_time_support(self, curent_time=None):
        """在curent_time时刻是否允许执行该任务"""
        return True

    def get_dependence_task(self):
        """判断当前任务对应的依赖项是否已经全部完成"""
        return None

    def whether_support_device_type(self, device_type):
        """任务是否支持device_type"""
        return False if device_type is None else True

    def register_config(self, xargs_dict=None):
        utils_logger.log("***************任务配置信息[register_config]:", xargs_dict)
        self.task_session = xargs_dict.get('taskcmd')

    def run_task(self):
        utils_logger.log('--->', self.__class__, '|',
                         utils_common.get_shanghai_time('%Y-%m-%d %H:%M:%S'))
        return True

    def release_after_task(self):
        # 任务执行完后的释放资源
        pass

    def notify_task_success(self):
        """更新任务状态"""
        pass

    def task_scheduler_failed(self, message="none message", email_title=u'异常信息', upload_files=None,
                              exception_info=None):
        """
            脚本执行错误，收集想过错误信息
            spot_desc_file指当前错误页面
        """
        # TODO:检查业务层调用一次task_scheduler_failed，这里为什么同一个文件会被添加多次？  ：暂时使用强制去重
        if upload_files is not None:
            self.upload_files.extend(upload_files)
        utils_logger.log("---> task_scheduler_failed in BaseTask with upload_files:",
                         list(set(self.upload_files)))
        error = {'message': message,
                 'task_name': self.task_session if self.task_session is not None else "None",
                 'threadid': str(threading.currentThread().getName()),
                 }

        send_content = json.dumps(error, ensure_ascii=False).encode('utf8')
        envs.zip_msg_within_files(email_title,
                                  send_content.decode() + "\n堆栈信息：\n"
                                  + ("None" if exception_info is None else exception_info),
                                  list(set(self.upload_files)))
