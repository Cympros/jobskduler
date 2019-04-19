# coding=utf-8

import json
import os
import sys
import traceback

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)

from helper import utils_common
from config import conf_modify
from config import email_send
from config import env_job
from config import utils_logger


class BaseJob():
    def __init__(self):
        self.upload_files = []  # 用于存储待上传的文件列表
        self.job_session = None
        self.xargs_dict = None

    def is_time_support(self, curent_time=None):
        """在curent_time时刻是否允许执行该任务"""
        return True

    def get_dependence_task(self):
        """判断当前任务对应的依赖项是否已经全部完成"""
        return None

    def get_support_device_types_with_task(self):
        """返回当前任务支持的设备类型"""
        return None

    def register_config(self, xargs_dict=None):
        utils_logger.log("***************任务配置信息[register_config]:", xargs_dict)
        self.xargs_dict = xargs_dict
        self.job_session = xargs_dict.get('job_session')

    def run_task(self):
        utils_logger.log('--->', self.__class__, '|', utils_common.get_shanghai_time('%Y-%m-%d %H:%M:%S'))
        return True

    def release_after_task(self):
        # 任务执行完后的释放资源
        pass

    def notify_job_success(self):
        """更新任务状态"""
        if self.job_session is None:
            utils_logger.log("---> notify_job_success： not support job_session for none")
            return
        utils_logger.log("---> update_task_state in class of BaseJob with session:[" + self.job_session + "]")
        # 更新该任务对应的today_repeat_count_left以及last_success_date
        today_date = int(utils_common.get_shanghai_time("%Y%m%d"))
        today_repeat_count_left = int(
            conf_modify.query(job_tag=self.job_session, key="today_repeat_count_left", default_value=0)) - 1

        conf_modify.put(job_tag=self.job_session, key="last_success_date", value=today_date)
        conf_modify.put(job_tag=self.job_session, key="today_repeat_count_left", value=today_repeat_count_left)
        utils_logger.log("---> After update###job_clz_path: ", self.job_session, "last_success_date: ", today_date,
                         "today_repeat_count_left: ", today_repeat_count_left)

    def job_scheduler_failed(self, message="none message", email_title=u'异常信息', upload_files=None, exception_info=None):
        """
            脚本执行错误，收集想过错误信息
            spot_desc_file指当前错误页面
        """
        # TODO:检查业务层调用一次job_scheduler_failed，这里为什么同一个文件会被添加多次？  ：暂时使用强制去重
        self.upload_files.extend(upload_files)
        utils_logger.log("---> job_scheduler_failed in BaseJob with upload_files:", list(set(self.upload_files)))
        error = {'message': message,
                 'task_name': self.job_session if self.job_session is not None else "None",
                 }

        send_content = json.dumps(error, encoding='utf-8', ensure_ascii=False)
        email_send.wrapper_send_email(title=email_title, content=send_content + "\n堆栈信息：\n" + (
            "None" if exception_info is None else exception_info), files=list(set(self.upload_files)))
