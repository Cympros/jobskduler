# coding=utf-8

import json
import os
import sys
import abc
import threading

# 添加python运行环境检测
if sys.version_info.major < 3:
    raise "Must be using Python 3"

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.insert(0, project_root_path)

from helper import utils_logger
from helper import utils_common
from helper import email_send


class BaseTask(abc.ABC):
    def __init__(self):
        self.upload_files = []  # 用于存储待上传的文件列表

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
        return self.handle_callback.read_config(self, "get_project_output_dir")

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
                 'task_name': self.__str__(),
                 'threadid': str(threading.currentThread().getName()),
                 }
        send_content = json.dumps(error, ensure_ascii=False)
        utils_logger.debug("error is below:", send_content)
        if len(list(set(self.upload_files))) <= 0:
            utils_logger.log("邮件必须包含附件文件")
        else:
            self.wrapper_send_email(title=email_title, content=str(send_content) + "\n堆栈信息：\n" + (
                "None" if exception_info is None else exception_info), files=list(set(self.upload_files)))

    def wrapper_send_email(self, title=None, content=None, files=None):
        mail_title = title if title is not None else u'python邮件标题'
        # files组合成数组
        wrapper_files = None
        if files is not None:
            if not isinstance(files, list):
                wrapper_files = [files]
            else:
                wrapper_files = files
        # 组装邮件内容[Git_Desc下格式]：【local分支】+【git_revision_number】+【orgin信息】+【commit_desc】
        mail_content = "Device_Host_Name:  " + utils_common.get_host_name() + "\n" \
                       + "Host_IP:   " + utils_common.get_real_host_ip() + "\n" \
                       + "Git_Desc:   " + json.dumps(utils_common.exec_shell_cmd("git branch -vv | grep '*'"),
                                                     ensure_ascii=False, ) + "\n\n" \
                       + "Content:    \n" + (content if content is not None else '来自python登录qq邮箱的测试邮件')

        # 发送邮件
        receiver_user = self.handle_callback.read_config(self, 'email_receiver')  # 邮件接收地址
        utils_logger.log("start to wrapper_send_email[" + receiver_user + "][" + mail_title + "]:", wrapper_files)
        # 发送email
        sender_host = self.handle_callback.read_config(self, 'email_sender_host')
        email_sender_user = self.handle_callback.read_config(self, 'email_sender_user')
        email_sender_pwd = self.handle_callback.read_config(self, 'email_sender_pwd')
        if receiver_user == "" or sender_host == "" or email_sender_user == "" or email_sender_pwd == "":
            utils_logger.log("参数配置错误", receiver_user, email_sender_user, email_sender_pwd, sender_host)
            return
        email_state = email_send.send_smtp_email(sender_host, email_sender_user, email_sender_pwd,
                                                 receiver_user, mail_title, mail_content, wrapper_files)
        if email_state is False:
            utils_logger.log("-------wrapper_send_email caught exceptiion-------")
