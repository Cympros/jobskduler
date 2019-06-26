# coding=utf-8

# 用于在指定时刻检查指定任务是否执行完成
import os
import sys
import collections as clc
from job_base import BaseJob as Base

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)

from config import conf_modify
from config import email_send
from config import env_job
from job.appium.utils import utils_android
from helper import utils_config_parser, utils_logger


class JobBrowserDeviceTimelyInfo(Base):
    """即时浏览设备信息"""

    def run_task(self):
        connected_device_info = "\n"
        disconected_device_info = "\n"
        device_conf_path = os.path.abspath(env_job.get_out_dir() + "/conf_device.ini")
        connected_android_devices = utils_android.get_connected_devcies()
        for device_tag in utils_config_parser.get_sessions(device_conf_path):
            device_item_info_map = utils_config_parser.get_map_within_session(device_conf_path, device_tag)
            connected_device_info += "[" + device_tag + "]:\n"
            for key, value in device_item_info_map.iteritems():
                connected_device_info += "    " + key + ":" + value + "\n"
        utils_logger.log(connected_device_info)


class JobCheckerAllTaskRunState(Base):
    '检查所有task的执行状态'

    def run_task(self):
        unrunnable_task_list = []

        email_content = "<目标执行成功次数-实际执行成功次数>/<目标执行成功次数>,执行成功率:<实际执行成功次数>/<实际执行次数>，[<脚本描述信息>]:<脚本路径>\n"
        circle_task_info = ""  # 循环任务
        normal_task_success = ""  # 普通任务-成功
        normal_task_failed = ""  # 普通任务-失败
        device_type_not_matched_task = ""  # 设备类型与任务不匹配
        app_not_installed_task = ""  # 未安装应用任务
        unrunnable_task = ""  # 不可执行任务
        retry_over_task = ""  # 重试次数操作次数的任务
        other_task = ""  # 其他任务

        all_job = conf_modify.query_jobs()
        all_job.sort()
        for job in all_job:  # 包含设备相关的job描述
            # 今日还剩余多少次没有执行完成
            job_path = conf_modify.query(job, "job_path")
            is_need_run = conf_modify.query(job, 'runnable')
            is_device_type_support = conf_modify.query(job, 'is_device_type_support')
            is_retry_count_over = conf_modify.query(job, "is_retry_count_over")
            daily_repeat_count = int(conf_modify.query(job, "daily_repeat_count", 0))
            today_repeat_count_left = int(conf_modify.query(job, "today_repeat_count_left", daily_repeat_count))
            today_total_run_number = int(conf_modify.query(job, "today_total_run_number", 0))

            output_info = "剩余执行次数：" + str(today_repeat_count_left) + "/" + str(daily_repeat_count) \
                          + "，执行成功率：" + str(daily_repeat_count - today_repeat_count_left) + "/" + str(
                today_total_run_number) \
                          + "，[" + conf_modify.query(job, 'job_name') + "]：" + job \
                          + "\n"
            """
            未完成任务拆分
            ---> 任务不可执行的
            ---> 设备类型不匹配的
            ---> 
            """
            if daily_repeat_count > 0 and today_repeat_count_left > 0:
                # 未完成任务
                if is_need_run is not None and is_need_run != 'true':
                    # 不可执行任务屏蔽设备，仅收集任务相关信息
                    if job_path not in unrunnable_task_list:
                        unrunnable_task_list.append(job_path)
                        unrunnable_task += "[" + conf_modify.query(job, 'job_name') + "]：" + job_path + "\n"
                elif is_device_type_support is not None and is_device_type_support != 'true':
                    device_type_not_matched_task += output_info
                elif is_retry_count_over is not None and is_retry_count_over == "true":
                    # 重试超过次数
                    retry_over_task += output_info
                #     先根据上面几种boolean状态过滤，再进行下面数据的整理：比如JobCheckerAllTaskRunState就不应该在android设备上执行
                elif job_path in ['job_normal.JobCheckerAllTaskRunState']:
                    other_task += output_info
                elif daily_repeat_count > 9999:
                    circle_task_info += output_info
                else:
                    normal_task_failed += output_info
            else:
                normal_task_success += output_info
        # 组装邮件内容
        email_title = u'TodayTaskFailed' if normal_task_failed != "" else u"今日任务已全部完成"
        utils_logger.log("---> wrapper_send_email", email_title)
        if normal_task_failed != "":
            email_content += "[未完成任务]：\n" + normal_task_failed + "\n"
        if retry_over_task != "":
            email_content += "[重试次数超过限制]：\n" + retry_over_task + "\n"
        if circle_task_info != "":
            email_content += "[循环任务]：\n" + circle_task_info + "\n"
        # if app_not_installed_task !="":
        #     email_content+="[设备上未安装对应应用]：\n"+app_not_installed_task+"\n"
        if unrunnable_task != "":
            email_content += "[不可执行任务]：\n" + unrunnable_task + "\n"
        ## 以下任务没有分析的必要
        email_content += "\n##################################################################################\n"
        if normal_task_success != "":
            email_content += "[已完成任务]：\n" + normal_task_success + "\n"
        if other_task != "":
            email_content += "[其他任务]：\n" + other_task + "\n"
        if device_type_not_matched_task != "":
            email_content += "[设备类型与任务不匹配任务]：\n" + device_type_not_matched_task + "\n"
        email_send.wrapper_send_email(title=email_title, content=email_content)
        return True

    def is_time_support(self, curent_time=None):
        # 每日检查时刻是每天晚上6点，早点不影响睡眠
        is_run_support = True if 1800 < curent_time else False
        utils_logger.log(str(curent_time) + "---> is_run_support(" + str(self.__class__) + "):" + (
            "True" if is_run_support else "False"))
        return is_run_support

class JobResetRunRetryModel(Base):
    """用于解决超过重试次数的任务"""

    def run_task(self):
        while True:
            all_job = conf_modify.query_jobs()
            # 筛选出超出重试次数的任务
            retry_over_tasks = []
            all_job.sort()
            for job_session in all_job:  # 包含设备相关的job描述
                is_retry_count_over = conf_modify.query(job_session, "is_retry_count_over", "false")
                # print job_session,is_retry_count_over
                if is_retry_count_over == "true":
                    retry_over_tasks.append(job_session)
            # 组建提示信息
            retry_over_task_tips = "今日重试次数已达上限任务列表：\n"
            for index, job_session in enumerate(retry_over_tasks):
                retry_over_task_tips += "\n" + str(index) + "：" + job_session
            retry_over_index = raw_input(retry_over_task_tips + "\n请选择对应索引以重置重试逻辑(索引下标越界触发程序退出)：")
            if retry_over_index.isdigit() is False:
                utils_logger.log("索引值非数字，请重新输入：", retry_over_index)
                continue
            retry_over_index = int(retry_over_index)
            if retry_over_index >= len(tasks) > 0:
                utils_logger.log("[" + str(retry_over_index) + "]任务索引不存在，退出程序...")
                break
            utils_logger.log("start to reset state for retry_over：", retry_over_tasks[retry_over_index])
            # reset
            daily_repeat_count = conf_modify.query(retry_over_tasks[retry_over_index], "daily_repeat_count")
            today_repeat_count_left = conf_modify.query(retry_over_tasks[retry_over_index], "today_repeat_count_left")
            if daily_repeat_count is not None and today_repeat_count_left is not None:
                conf_modify.put(retry_over_tasks[retry_over_index], "today_total_run_number",
                                int(daily_repeat_count) - int(today_repeat_count_left))
            else:
                conf_modify.put(retry_over_tasks[retry_over_index], "today_total_run_number", 0)
            conf_modify.put(retry_over_tasks[retry_over_index], "is_retry_count_over", "false")
            utils_logger.log("-----------------------------------------------\n")


class JobClearUnUseDevice(Base):
    def run_task(self):
        """以设备为维度，清空不再使用的设备下对应的所有任务"""
        device_dict = clc.defaultdict(list)
        for item_job in conf_modify.query_jobs():
            # 按照device_tag分组
            item_job_splits = item_job.split("&&", 1)  # 以&&拆分为两个
            device_dict[item_job_splits[0]].append(item_job)
        # 遍历字典，读取设备信息
        device_conf_path = os.path.abspath(env_job.get_out_dir() + "/conf_device.ini")
        job_conf_path = os.path.abspath(env_job.get_out_dir() + "/conf_job.ini")
        while True:
            input_tips = "设备对应的设备号："
            device_list = list(device_dict.iterkeys())
            print device_list
            for index, device_tag in enumerate(device_list):
                input_tips += "\n" + str(index) + "：" + device_tag
            device_index_selected = raw_input(input_tips + "\n请选择设备对应索引以删除任务(索引下标越界触发程序退出)：")
            if device_index_selected.isdigit() is False:
                utils_logger.log("索引值非数字，请重新输入：", device_index_selected)
                continue
            device_index_selected = int(device_index_selected)
            if device_index_selected >= len(tasks) > 0:
                utils_logger.log("[" + str(device_index_selected) + "]设备索引不存在，退出程序...")
                break
            # 查看设备信息
            config_map = utils_config_parser.get_map_within_session(device_conf_path,
                                                                    device_list[device_index_selected])
            is_confirm_delete = raw_input("确认删除该设备下对应的所有任务吗？(y/n)\n" + str(config_map) + "\n")
            if is_confirm_delete != "y":
                continue
            else:
                utils_logger.log("删除该设备对应的所有任务")
                for task_within_device in device_dict[device_list[device_index_selected]]:
                    utils_logger.log("start to delete task: " + task_within_device)
                    utils_config_parser.delete_session(job_conf_path, task_within_device)
            utils_logger.log("-----------------------------------------------\n")


if __name__ == "__main__":
    tasks = ['JobCheckerAllTaskRunState', 'JobBrowserDeviceTimelyInfo', 'JobClearUnUseDevice', 'JobResetRunRetryModel']
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
        task_name = tasks[task_index_selected]
        job = eval(task_name + '()')
        job.run_task()
