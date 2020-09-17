# coding=utf-8

import os
import sys

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../')
sys.path.insert(0, project_root_path)

from tasks.task_base import BaseTask


class AbsAbsBasicPCTask(BaseTask):

    def __init__(self):
        BaseTask.__init__(self)

    def run_task(self, _handle_callback):
        return BaseTask.run_task(self, _handle_callback)

    def task_scheduler_failed(self, message="none message", email_title=u'异常信息', upload_files=None,
                              exception_info=None):
        BaseTask.task_scheduler_failed(self, message, email_title, upload_files, exception_info)

    def whether_support_device_type(self, device_type):
        if BaseTask.whether_support_device_type(self, device_type) is False:
            return False
        if device_type != "pc":
            return False
        return True
