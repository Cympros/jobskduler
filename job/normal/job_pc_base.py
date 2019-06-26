# coding=utf-8

import os
import sys

root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../')
sys.path.append(root_path)

from job.job_base import BaseJob


class PcBaseJob(BaseJob):

    def __init__(self):
        BaseJob.__init__(self)

    def run_task(self):
        return BaseJob.run_task(self)

    def job_scheduler_failed(self, message="none message", email_title=u'异常信息', upload_files=None, exception_info=None):
        BaseJob.job_scheduler_failed(self, message, email_title, upload_files, exception_info)

    def whether_support_device_type(self, device_type):
        if BaseJob.whether_support_device_type(self, device_type) is False:
            return False
        if device_type != "pc":
            return False
        return True
