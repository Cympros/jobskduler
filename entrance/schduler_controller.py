# coding=utf-8
# 任务终端控制器，用于安排各个job
import os
import sys
import json

root_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(root_path)
sys.path.append(root_path + '/job/appium/task')
sys.path.append(root_path + '/job/normal')

from config.dbhelper import DataBaseOpenHelper
from config import env_job
from config import conf_modify
from utils import utils_logger
from job.appium.utils import utils_android


class JobSchdulerController(object):

    def __init__(self):
        self.db_helper = DataBaseOpenHelper(env_job.get_out_dir() + "/schduler.db")
        self.db_helper.exec_sql('''create table if not exists tbjob
        (taskcmd char(50)  not null ,
        fsthreadid char(50) not null,
        primary key(fsthreadid,taskcmd));''')
        self.db_helper.exec_sql('''create table if not exists tbtask
        (taskcmd char(50) not null primary key,
        taskname char(50),
        dailycount integer default 1);''')
        self.db_helper.exec_sql('''create table if not exists tbthreadinfo
        (threadid char(50) primary key,
        device_name char(50),
        device_type char(50) not null)''')

    def add_task(self):
        """添加任务"""
        device_type_index = raw_input("请输入设备类型(0:android,1:pc)")
        if device_type_index != '0' and device_type_index != '1':
            utils_logger.log("不支持添加的设备类型", device_type_index)
            return
        device_type = "android" if device_type_index != '1' else "pc"
        if device_type == "android":
            # 插入所有android设备
            for connect_device in utils_android.get_connected_devcies():
                temp_threadid = utils_android.get_device_tag(connect_device) + ".thread"
                self.db_helper.exec_sql(
                    "replace into tbthreadinfo(threadid,device_name,device_type) values('" + temp_threadid + "','" + connect_device + "','" + device_type + "')")
                # 展示所有连接设备
                utils_logger.log("线程标识：" + temp_threadid, "连接设备：" + connect_device)
            threadid = raw_input("请输入线程标识:")
        else:
            threadid = "pc.thread"
            self.db_helper.exec_sql(
                "replace into tbthreadinfo(threadid,device_type) values('" + threadid + "','" + device_type + "')")
        if not threadid.endswith(".thread"):
            utils_logger.log("线程唯一标识不合法")
            return

        # 插入tbtask
        for task_item in conf_modify.query_jobs():
            self.db_helper.exec_sql("insert or replace into tbtask(taskcmd,taskname,dailycount) values ('"
                                    + task_item + "','"
                                    + conf_modify.query(task_item, 'job_name').replace("'", "*") + "','"
                                    + conf_modify.query(task_item, "daily_repeat_count", '1') + "')")
            if conf_modify.query(task_item, "runnable", "false") == 'true':
                job_exists_sql = "select count(*) as count from tbjob where fsthreadid='" + threadid \
                                 + "' and taskcmd='" + task_item + "'"
                list_dict = self.db_helper.exec_sql(job_exists_sql)
                if int(list_dict[0]['count']) <= 0:
                    utils_logger.log("任务：", task_item)
        taskcmd = raw_input("请输入任务唯一标识")
        if taskcmd == "":
            utils_logger.log("任务标识不合理")
            return

        self.db_helper.exec_sql(
            "insert or replace into tbjob(taskcmd,fsthreadid) values ('" + taskcmd + "','" + threadid + "');")

    def edit_task(self):
        """编辑任务"""
        pass

    def del_task(self):
        self.db_helper.exec_sql('''delete from tbjob;''')
        self.db_helper.exec_sql('''delete from tbthreadinfo;''')

    def exec_task(self):
        """执行任务"""
        utils_logger.log(json.dumps(self.db_helper.exec_sql('select * from tbjob;')))


if __name__ == '__main__':
    JobSchdulerController().add_task()
