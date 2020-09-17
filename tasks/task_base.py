# coding=utf-8

import json
import os
import sys
import threading

# 添加python运行环境检测
if sys.version_info.major < 3:
    raise "Must be using Python 3"

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.insert(0, project_root_path)

from helper import utils_logger
from helper import utils_common


class BaseTask():
    def __init__(self):
        self.upload_files = []  # 用于存储待上传的文件列表
        self.task_session = None

    def get_dependence_task(self):
        """判断当前任务对应的依赖项是否已经全部完成"""
        return None

    def whether_support_device_type(self, device_type):
        """任务是否支持device_type"""
        return False if device_type is None else True

    def run_task(self, _handle_callback):
        self.handle_callback = _handle_callback
        return True

    def get_project_output_dir(self):
        return self.handle_callback.read_config(None, "get_project_output_dir")

    def release_after_task(self):
        # 任务执行完后的释放资源
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
        utils_logger.log("task_scheduler_failed.upload_files",
                         list(set(self.upload_files)))
        error = {'message': message,
                 'task_name': self.task_session if self.task_session is not None else "None",
                 'threadid': str(threading.currentThread().getName()),
                 }

        send_content = json.dumps(error, ensure_ascii=False).encode('utf8')
        utils_common.zip_msg_within_files(self.get_project_output_dir(), email_title,
                                          send_content.decode() + "\n堆栈信息：\n"
                                          + ("None" if exception_info is None else exception_info),
                                          list(set(self.upload_files)))
