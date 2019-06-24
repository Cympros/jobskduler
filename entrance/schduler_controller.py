# coding=utf-8
# 任务终端控制器，用于安排各个job
import os
import sys
import json
import random
import threading
import traceback

root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../')
sys.path.append(root_path)
sys.path.append(root_path + '/job/appium/task')
sys.path.append(root_path + '/job/normal')
sys.path.append(root_path + '/job')

from config.dbhelper import DataBaseOpenHelper
from config import env_job
from config import conf_modify
from helper import utils_logger
from job.appium.utils import utils_android


class JobSchdulerController(object):

    def __init__(self):
        self.db_path = env_job.get_out_dir() + "/schduler.db"
        self.db_helper = DataBaseOpenHelper(self.db_path)
        self.db_helper.exec_sql('''create table if not exists tbjob
        (taskcmd char(50)  not null ,
        fsthreadid char(50) not null,
        primary key(fsthreadid,taskcmd));''')
        self.db_helper.exec_sql('''create table if not exists tbtask
        (taskcmd char(50) not null primary key,
        taskname char(50),
        runnable char(50),
        dailycount integer default 1);''')
        self.db_helper.exec_sql('''create table if not exists tbthreadinfo
        (threadid char(50) primary key,
        device_name char(50),
        device_type char(50) not null,
        appium_port integer,
        appium_port_bp integer)''')

    def add_task(self):
        """添加任务"""
        # 插入设备信息
        for device_type in ['android', 'pc']:
            if device_type == "android":
                # 插入所有android设备
                for connect_device in utils_android.get_connected_devcies():
                    self.db_helper.exec_sql(
                        "replace into tbthreadinfo(threadid,device_name,device_type,appium_port,appium_port_bp) "
                        "values("
                        + "'" + utils_android.get_device_tag(connect_device) + "." + device_type + ".thread" + "',"
                        + "'" + connect_device + "',"
                        + "'" + device_type + "',"
                        + str(self.search_appium_port(True)) + ","
                        + str(self.search_appium_port(False))
                        + ")")
            else:
                self.db_helper.exec_sql(
                    "replace into tbthreadinfo(threadid,device_type) values('"
                    + device_type + ".thread"
                    + "','" + device_type + "')")

        # 插入tbtask
        for task_item in conf_modify.query_jobs():
            self.db_helper.exec_sql("insert or replace into tbtask(taskcmd,taskname,runnable,dailycount) values ('"
                                    + task_item + "','"
                                    + conf_modify.query(task_item, 'job_name').replace("'", "*") + "','"
                                    + conf_modify.query(task_item, "runnable", "true") + "','"
                                    + conf_modify.query(task_item, "daily_repeat_count", '1') + "')")
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

    def edit_task(self):
        """编辑任务"""
        pass

    def del_task(self):
        self.db_helper.exec_sql('''delete from tbjob;''')
        self.db_helper.exec_sql('''delete from tbthreadinfo;''')

    def exec_task(self):
        """执行任务"""
        utils_logger.log("##########exec_task")
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

    def exec_single_task(self):
        job_path = 'job_appium_qutoutiao.JobAppiumQtoutiaoCoreShiduanJiangli'
        mod_str, _sep, class_str = job_path.rpartition('.')
        print "##################", "\"" + mod_str + "\"", root_path
        __import__(mod_str)
        print "##################", "\"" + mod_str + "\"", root_path
        module_clz = getattr(sys.modules[mod_str], class_str)
        cls_obj = module_clz()
        if cls_obj.run_task() is True:
            cls_obj.notify_job_success()
        print "##################", "\"" + mod_str + "\"", root_path


def device_thread_loop(*jobs):
    job_list = list(jobs)
    random.shuffle(job_list)
    for job_item in job_list:
        if job_item['device_type'] != 'android':
            continue

        flag = False
        for device_connect in utils_android.get_connected_devcies():
            print job_item, device_connect
            if device_connect == job_item.get('device_name'):
                flag = True
        if flag is False:
            utils_logger.log("device_thread_loop 设备不在线")
            return

        try:
            job_path = job_item['taskcmd']
            # 实例化job类
            mod_str, _sep, class_str = job_path.rpartition('.')
            print "##################", "\"" + mod_str + "\"", root_path
            __import__(mod_str)
            print "##################", "\"" + mod_str + "\"", root_path
            module_clz = getattr(sys.modules[mod_str], class_str)
            cls_obj = module_clz()
            cls_obj.register_config(job_item)
            if cls_obj.run_task() is True:
                cls_obj.notify_job_success()
        except:
            traceback.print_stack()


if __name__ == '__main__':
    controller = JobSchdulerController()
    tasks = ['add_task', 'exec_task', 'del_task', 'exec_single_task']
    while True:
        input_info = "------------------------执行任务列表-----------------------\n"
        for index, task_item in enumerate(tasks):
            input_info += str(index) + "：" + task_item + "\n"
        task_index_selected = raw_input(input_info + "请选择需运行任务对应索引(索引下标越界触发程序退出)：")
        if task_index_selected.isdigit() is False:
            utils_logger.log("索引值非数字，请重新输入：", task_index_selected)
            continue
        task_index_selected = int(task_index_selected)
        if task_index_selected >= len(tasks) > 0:
            utils_logger.log("[" + str(task_index_selected) + "]任务索引不存在，退出程序...")
            break
        func_name = tasks[task_index_selected]
        if hasattr(controller, func_name):
            func = getattr(controller, func_name)
            func()
