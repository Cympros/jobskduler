#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import sys
import time
import subprocess
import thread

root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../')
sys.path.append(root_path)

from helper import utils_logger, utils_common
from job.appium.utils import utils_android
from helper.dbhelper import DataBaseOpenHelper
from config import env_job


# def iter_module_files():
#     for module in sys.modules.values():
#         filename = getattr(module, '__file__', None)
#         if filename:
#             if filename[-4:] in ('.pyo', '.pyc'):
#                 filename = filename[:-1]
#             yield filename
#
#
# def is_any_file_changed(mtimes):
#     for filename in iter_module_files():
#         try:
#             mtime = os.stat(filename).st_mtime
#         except IOError:
#             continue
#         old_time = mtimes.get(filename, None)
#         if old_time is None:
#             mtimes[filename] = mtime
#         elif mtime > old_time:
#             return 1
#     return 0

def is_code_update():
    """代码是否有更新"""
    res, error = utils_common.exec_shell_cmd("timeout 15 git pull")
    if res is not None:
        if res.find('Already up to date.') != -1:
            # 代码已经是最新
            return 0
        elif res.find('Fast-forward') != -1:
            utils_logger.log("JobCheckCodeUpdate#run_task 检测到代码需要更新")
            return 1
    else:
        utils_logger.log("JobCheckCodeUpdate#run_task 检测到异常", "res:[" + str(res) + "]", "error:[" + str(error) + "]")
        return 1


def is_connect_new_devices():
    """是否连接新设备"""
    connect_devices = utils_android.get_connected_devcies()
    if connect_devices is None:
        return 0
    db_helper = DataBaseOpenHelper(env_job.get_db_path())
    for device in connect_devices:
        t_thread_id = utils_android.get_device_tag(device) + ".android.thread"
        count_within_device = db_helper.exec_sql(
            "select count(1) as count from tbthreadinfo where threadid = '" + t_thread_id + "'")
        if int(count_within_device[0]['count']) <= 0:
            # 还不存在该设备，重新添加任务
            return 1
    return 0


def is_need_reload_module():
    if is_code_update() == 1 or is_connect_new_devices() == 1:
        return 1
    return 0


def start_change_detector():
    while 1:
        if is_need_reload_module():
            time.sleep(10)
            sys.exit(3)
        time.sleep(10)


def restart_with_reloader():
    while 1:
        args = [sys.executable] + sys.argv
        new_env = os.environ.copy()
        new_env['RUN_FLAG'] = 'true'
        exit_code = subprocess.call(args, env=new_env)
        if exit_code != 3:
            return exit_code


def run_with_reloader(runner):
    if os.environ.get('RUN_FLAG') == 'true':
        thread.start_new_thread(runner, ())
        try:
            start_change_detector()
        except KeyboardInterrupt:
            pass
    else:
        try:
            sys.exit(restart_with_reloader())
        except KeyboardInterrupt:
            pass
