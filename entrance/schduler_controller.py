# coding=utf-8
# 任务终端控制器，用于安排各个job
import os
import sys
import json
import time
import random
import threading
import traceback
import subprocess

root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../')
sys.path.append(root_path)
sys.path.append(root_path + '/job/appium/task')
sys.path.append(root_path + '/job/normal/task')
sys.path.append(root_path + '/job')

from helper.dbhelper import DataBaseOpenHelper
from config import env_job
from helper import utils_logger
from job.appium.utils import utils_android
from helper import utils_common
from helper import utils_config_parser
from config import email_send


class JobSchdulerController(object):

    def __init__(self):
        self.db_path = env_job.get_db_path()
        self.db_helper = None

    def get_db_helper(self):
        utils_logger.log("JobSchdulerController#get_db_helper")
        db_helper = DataBaseOpenHelper(self.db_path)
        db_helper.exec_sql('''create table if not exists tbjob
                (taskcmd char(50)  not null ,
                fsthreadid char(50) not null,
                primary key(fsthreadid,taskcmd));''')
        db_helper.exec_sql('''create table if not exists tbtask
                (taskcmd char(50) not null primary key,
                taskname char(50),
                runnable char(50),
                dailycount integer default 1);''')
        db_helper.exec_sql('''create table if not exists tbthreadinfo
                (threadid char(50) primary key,
                device_name char(50),
                device_type char(50) not null,
                appium_port integer,
                appium_port_bp integer)''')
        return db_helper

    def add_task(self):
        """添加任务"""
        # 插入设备信息
        if self.db_helper is None:
            self.db_helper = self.get_db_helper()

        utils_logger.log("##########JobSchdulerController#add_task [tbthreadinfo]开始插入线程信息")
        for device_type in ['android', 'pc']:
            if device_type == "android":
                # 插入所有android设备
                connected_devices = utils_android.get_connected_devcies()
                if connected_devices is not None:
                    for connect_device in connected_devices:
                        t_thread_id = utils_android.get_device_tag(connect_device) + "." + device_type + ".thread"
                        appium_port = str(self.search_appium_port(True))
                        appium_port_bp = str(self.search_appium_port(False))
                        insert_sql = "replace into tbthreadinfo(threadid,device_name,device_type,appium_port,appium_port_bp) " \
                                     + "values(" \
                                     + "'" + t_thread_id + "'," \
                                     + "'" + connect_device + "'," \
                                     + "'" + device_type + "'," \
                                     + appium_port + "," \
                                     + appium_port_bp \
                                     + ")"
                        utils_logger.log("插入线程", insert_sql)
                        self.db_helper.exec_sql(insert_sql)
            else:
                self.db_helper.exec_sql(
                    "replace into tbthreadinfo(threadid,device_type) values('"
                    + device_type + ".thread"
                    + "','" + device_type + "')")

        # 插入tbtask
        utils_logger.log("##########JobSchdulerController#add_task [tbtask]开始插入task信息")
        for task_item in utils_config_parser.get_sessions(env_job.get_job_config_path()):
            runnable = utils_config_parser.get_value(env_job.get_job_config_path(), task_item, "runnable", "true")
            if runnable != 'true':
                self.db_helper.exec_sql("delete from tbjob where taskcmd='" + task_item + "'")
            else:
                taskname = utils_config_parser.get_value(env_job.get_job_config_path(), task_item, 'job_name') \
                    .replace("'", "*")
                daily_count = utils_config_parser.get_value(env_job.get_job_config_path(), task_item,
                                                            "daily_repeat_count", '1')
                self.db_helper.exec_sql("insert or replace into tbtask(taskcmd,taskname,runnable,dailycount) values ('"
                                        + task_item + "','"
                                        + taskname + "','"
                                        + runnable + "','"
                                        + daily_count + "')")
        # 插入job
        for threadid_item in self.db_helper.exec_sql('select threadid from tbthreadinfo'):
            for taskcmd_item in self.db_helper.exec_sql("select taskcmd from tbtask where runnable='true'"):
                list_dict = self.db_helper.exec_sql("select count(1) as count from tbjob where fsthreadid='"
                                                    + threadid_item['threadid']
                                                    + "' and taskcmd='" + taskcmd_item['taskcmd'] + "'")
                if int(list_dict[0]['count']) <= 0:
                    utils_logger.log("插入任务：", threadid_item['threadid'], taskcmd_item['taskcmd'])
                    self.db_helper.exec_sql("insert or replace into tbjob(taskcmd,fsthreadid) values ('"
                                            + taskcmd_item['taskcmd'] + "','"
                                            + threadid_item['threadid'] + "');")
        utils_logger.log(json.dumps(self.db_helper.exec_sql('select * from tbjob;')))

    def search_appium_port(self, is_odd):
        """
        :param is_odd: 是否单数
        :return:
        """
        for port in range((4723 if is_odd is True else 4724), 8000, 2):
            list_dict = self.db_helper.exec_sql("select count(1) as count from tbthreadinfo where appium_port="
                                                + str(port) + " or appium_port_bp=" + str(port))
            if int(list_dict[0]['count']) <= 0:
                return port

    def exec_task(self):
        """执行任务"""
        # 关闭appium进程
        utils_common.exec_shell_cmd(
            '''ps -ef | grep "appium" | grep -v -E "grep|$$" | awk  '{print "kill -9 " $2}' | sh''')

        if self.db_helper is None:
            self.db_helper = self.get_db_helper()
        self.add_task()  # 重新导入任务

        utils_logger.log("##########JobSchdulerController#exec_task")
        thread_maps = {}
        for threadid_item in self.db_helper.exec_sql('select distinct fsthreadid from tbjob;'):
            thread_name = threadid_item['fsthreadid']
            device_thread = thread_maps.get(thread_name)
            if device_thread is not None and device_thread.is_alive() is True:
                # 表示该线程还在执行任务，继续等待
                return
            else:
                job_infos = self.db_helper.exec_sql(
                    "select tbjob.taskcmd,tbthreadinfo.* from tbjob inner join tbthreadinfo "
                    + "on tbjob.fsthreadid=tbthreadinfo.threadid "
                    + "where tbjob.fsthreadid='" + thread_name + "';")
                if job_infos is None:
                    utils_logger.log("exec_task 任务数据为空")
                    continue
                # utils_logger.log("######exec_task create new thread", thread_name)
                device_thread = threading.Thread(target=device_thread_loop,
                                                 args=(job_infos),
                                                 name=thread_name)
                # 设置为后台线程，这样主线程结束时能自动退出
                device_thread.setDaemon(True)
                device_thread.start()

                thread_maps[thread_name] = device_thread

    def clear(self):
        utils_logger.log("#####JobSchdulerController#clear ")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def exec_single_task(self):
        job_path = 'job_normal.JobCheckerAllTaskRunState'
        mod_str, _sep, class_str = job_path.rpartition('.')
        # print "##################", "\"" + mod_str + "\"", root_path
        __import__(mod_str)
        # print "##################", "\"" + mod_str + "\"", root_path
        module_clz = getattr(sys.modules[mod_str], class_str)
        cls_obj = module_clz()
        if cls_obj.run_task() is True:
            cls_obj.notify_job_success()
        # print "##################", "\"" + mod_str + "\"", root_path

    def check_env_dependence(self):
        utils_logger.log("#####JobSchdulerController#check_env_dependence 检查环境依赖")
        p = subprocess.Popen(["bash", os.path.abspath(root_path + "/config/schduler_doctor.sh")])
        p.communicate()  # 这一步表示等待Popen执行完成
        if p.returncode != 0:
            utils_logger.log("#check_env_dependence# Non zero exit code executing")
        return p.stdout


def device_thread_loop(*jobs):
    job_list = list(jobs)
    utils_logger.log("#####JobSchdulerController#device_thread_loop", job_list)
    while True:
        # 记录每轮任务的执行时间，执行过短的进行休眠操作
        foreach_start_time = utils_common.get_shanghai_time()
        random.shuffle(job_list)
        for job_item in job_list:
            try:
                # if job_item['threadid'] != 'e7604cfbe2ca4adf.android.thread':
                #     # utils_logger.log(job_item)
                #     continue

                # 实例化job类
                # utils_logger.log("############################",job_item)
                job_path = job_item['taskcmd']
                mod_str, _sep, class_str = job_path.rpartition('.')
                __import__(mod_str)
                module_clz = getattr(sys.modules[mod_str], class_str)
                cls_obj = module_clz()
                if cls_obj.whether_support_device_type(job_item['device_type']) is False:
                    utils_logger.log("不支持执行该任务", job_path)
                    continue

                cls_obj.register_config(job_item)
                if cls_obj.run_task() is True:
                    cls_obj.notify_job_success()
                # 环境清理
                cls_obj.release_after_task()
            except Exception as exception:
                utils_logger.log(traceback.format_exc())
                email_send.wrapper_send_email(title=u'异常信息[' + exception.__class__.__name__ + "]",
                                              content="反射调用脚本错误:" + job_path + "\n" + traceback.format_exc())
        foreach_end_time = utils_common.get_shanghai_time()
        if foreach_end_time - foreach_start_time < 20:
            utils_logger.log("##### 任务循环过快，休眠5分钟:", foreach_end_time - foreach_start_time)
            time.sleep(5 * 60)


def runner():
    utils_logger.log("[" + str(os.getpid()) + "]enter...")
    JobSchdulerController().exec_task()
    utils_logger.log("[" + str(os.getpid()) + "]runner.")


if __name__ == '__main__':
    from helper.autoreload import run_with_reloader

    run_with_reloader(runner)
