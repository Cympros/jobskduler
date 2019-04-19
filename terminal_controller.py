# coding=utf-8
# 任务终端控制器，用于安排各个job的执行时间以及执行次数
import os
import sys
import time
import signal
import random
import threading
import traceback
from contextlib import contextmanager

root_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(root_path)
sys.path.append(root_path + '/job/appium/task')
sys.path.append(root_path + '/job')

from config import conf_modify
from config import email_send
from config import env_job
from config import utils_logger
from helper import utils_config_parser
from helper import utils_common
from job.appium.helper import utils_android


def run_job():
    utils_logger.log(">>>>>>>>>>>>>>>>>>>", "pid[" + str(utils_common.exec_shell_cmd('echo $$')) + "]",
                     utils_common.get_shanghai_time('%Y-%m-%d %H:%M:%S'), "<<<<<<<<<<<<<<<<<<<")
    # 处理新增设备时无法及时感知
    while True:
        # 查询所有已连接设备，以设备为维度划分多线程
        generate_thread_if_not_exist('#pc_devices', "pc")
        # 遍历已连接的android设备
        connected_android_devices = utils_android.get_connected_devcies()
        for connect_device in connected_android_devices:
            generate_thread_if_not_exist(connect_device, "android")
        # 遍历历史连接设备,这里的history_device可能是经过":" -> "[config_divider]"的转换逻辑
        history_devices_map = utils_config_parser.get_map_within_session(
            os.path.abspath(env_job.get_out_dir() + "/conf_static.ini"), 'history_connected_device')
        for history_device, device_type in history_devices_map.iteritems():
            # utils_logger.log(history_device,"[",device_type,"]")
            if device_type != "android":
                # utils_logger.log("设备不满足重连类型：",history_device)
                continue
            actual_device = history_device.replace("[config_divider]", ":")
            if connected_android_devices is None or actual_device not in connected_android_devices:
                utils_logger.log("重连设备", actual_device)
                # TODO:检测该设备是否是adb:网络连接方式
                cmd = "adb connect " + actual_device
                utils_logger.log("---> [exec_shell_cmd]:", cmd)
                utils_common.exec_shell_cmd(cmd)
        # 检查代码是否有更新，若存在更新则结束死循环，让bash脚本重启python脚本
        # 方案：获取当前git的本地分支与远程分支下最新的commitid,若两个commitid不一致，则退出循环，触发python脚本重启
        # TODO:分支名暂时写死
        if utils_common.exec_shell_cmd("git fetch && git rev-parse develop") != utils_common.exec_shell_cmd(
                "git fetch && git rev-parse origin/develop"):
            utils_logger.log("检测到有代码更新，触发python脚本的更新操作....")
            # TODO：记得校验"git pull"的执行结果，否则会进入死循环，始终无法执行具体任务
            git_pull_response = utils_common.exec_shell_cmd("git pull")
            utils_logger.log("执行结果[git pull]", git_pull_response)
            email_send.wrapper_send_email(title="Git更新", content="git pull执行结果:\n" + git_pull_response)
            break
        # 休眠
        utils_logger.log("等待下次设备自动感知(5分钟).............")
        time.sleep(5 * 60)


thread_maps = {}


# 构建线程
def generate_thread_if_not_exist(device, device_type):
    """构建线程
    @:param device_type :'android','pc'"""
    # utils_logger.log("已连接的设备：",connect_device)
    # 记录历史登录设备,保存在conf_static.ini/history_connected_device下，以"device = device_type"保留数据
    static_conf_path = os.path.abspath(env_job.get_out_dir() + "/conf_static.ini")
    # 由于ConfigParser的key中不允许包含":"、"="等字符，需要特殊处理下
    utils_config_parser.put_value(static_conf_path, "history_connected_device", device.replace(":", "[config_divider]"),
                                  device_type)
    utils_logger.log("[generate_thread_if_not_exist]", device, device_type)
    # 用以解决同一款android设备以不同的adb方式连接导致的任务重复执行
    if device_type != "android":
        device_tag = device
    else:
        device_tag = utils_android.get_device_tag(device)
    if device_tag is None:
        utils_logger.log("generate_thread_if_not_exist:无法获取设备的唯一标识")
        return

    # 根据device_tag保存设备信息
    device_conf_path = os.path.abspath(env_job.get_out_dir() + "/conf_device.ini")
    utils_config_parser.put_value(device_conf_path, device_tag, "device", device)
    utils_config_parser.put_value(device_conf_path, device_tag, "device_type", device_type)
    if device_type == "android":
        utils_config_parser.put_value(device_conf_path, device_tag, "device_brand",
                                      utils_android.get_brand_by_device(device))
        utils_config_parser.put_value(device_conf_path, device_tag, "device_model",
                                      utils_android.get_model_by_device(device))
        utils_config_parser.put_value(device_conf_path, device_tag, "device_resolution",
                                      utils_android.get_resolution_by_device(device))

    thread_name = device_tag + ".thread"
    utils_logger.log("generate_thread_if_not_exist 线程名称：" + thread_name)
    device_thread = thread_maps.get(thread_name)
    if device_thread is not None and device_thread.is_alive() is True:
        # 表示该线程还在执行任务，继续等待
        return
    else:
        device_thread = threading.Thread(target=device_thread_loop, args=(device, device_tag, device_type),
                                         name=thread_name)
        # 设置为后台线程，这样主线程结束时能自动退出
        device_thread.setDaemon(True)
        thread_maps[thread_name] = device_thread
        utils_logger.log("线程信息：", thread_maps)
        device_thread.start()


# 新线程执行job任务
def device_thread_loop(connect_device, device_tag, device_type):
    """检查设备类型"""
    # for index in range(1):
    while True:
        # utils_logger.log("device_thread_loop->" + connect_device)
        # time.sleep(18 * 60)
        # 遍历执行job配置信息
        support_job_path = env_job.get_module_root_path() + "/config/job.config"
        support_tasks = utils_config_parser.get_sessions(support_job_path)
        random.shuffle(support_tasks)  # 打乱list集合(即jobs)
        foreach_start_time = utils_common.get_shanghai_time()
        for job in support_tasks:
            job_config_map = utils_config_parser.get_map_within_session(support_job_path, job)
            exec_task(connect_device, device_tag, device_type, job, job_config_map)
        foreach_end_time = utils_common.get_shanghai_time()
        if foreach_end_time - foreach_start_time < 5:
            utils_logger.append_log("---> 任务循环过快，执行休眠策略[", device_tag, "]:", foreach_end_time - foreach_start_time)
            time.sleep(5 * 60)


# 执行具体的任务操作任务
def exec_task(device, device_tag, device_type, job, job_config_map):
    # 判断android设备是否在充电
    if device_type == "android":
        battery_status = utils_android.get_battery_status_by_device(device)
        if battery_status is None or battery_status != "true":
            utils_logger.log("设备不再充电，跳过该任务", device_tag)
            return

    job_session = device_tag + "&&" + job  # device配合job定义的job_session，用于表示每个设备上的任务

    # 同步配置
    conf_modify.put(job_session, "job_path", job)  # 定义脚本的执行路径
    conf_modify.put(job_session, "job_name", job_config_map["job_name"])
    conf_modify.put(job_session, "daily_repeat_count",
                    1 if job_config_map.get('daily_repeat_count') is None else job_config_map.get('daily_repeat_count'))
    conf_modify.put(job_session, "runnable",
                    'true' if job_config_map.get("runnable") is None else job_config_map.get("runnable"))

    job_path = conf_modify.query(job_session, "job_path")
    job_name = conf_modify.query(job_session, 'job_name')
    daily_repeat_count = int(conf_modify.query(job_session, 'daily_repeat_count'))
    is_need_run = conf_modify.query(job_session, 'runnable')
    is_device_type_support = conf_modify.query(job_session, 'is_device_type_support', "true")

    if is_need_run != 'true':
        utils_logger.log("该任务已废弃", job_path)
        return

    if is_device_type_support != "true":
        utils_logger.log("任务与设备类型不匹配", device_type, job_session)
        return

    utils_logger.log(
        "#####################################################################################################")
    # 初始化状态
    today_date = int(utils_common.get_shanghai_time("%Y%m%d"))
    last_success_date = conf_modify.query(job_tag=job_session, key="last_success_date")
    if last_success_date is None or int(last_success_date) < int(today_date):
        # 每日配置还原
        conf_modify.put(job_tag=job_session, key="today_repeat_count_left", value=daily_repeat_count)
    else:
        # 查询是否还允许执行脚本:查询今日剩余次数，特指成功执行的次数
        today_repeat_count_left = int(conf_modify.query(job_session, key="today_repeat_count_left"))
        if today_repeat_count_left <= 0:
            utils_logger.log("----> start to run job(" + job_name + ")：kpi of today finish,exit")
            return
            # 重置上次执行的时间
    last_exec_date = conf_modify.query(job_session, "last_exec_date")
    if last_exec_date is None or int(last_exec_date) < int(today_date):
        utils_logger.log("该任务是今日首次执行，需要重置today_total_run_number")
        conf_modify.put(job_tag=job_session, key="today_total_run_number", value=0)

    # utils_logger.log("---> Task[name,job_path,runnable,daily_repeat_count]:", job_name, ",", job_clz_path, ",", is_need_run, ",", daily_repeat_count
    # 执行脚本任务
    utils_logger.log("[" + job_name + "]----> start to run job：" + job_path + "...................")

    # 反射调用脚本
    try:
        # 判断今日任务尝试执行次数是否已达到上限
        today_total_run_number = int(conf_modify.query(job_session, 'today_total_run_number', 0))
        daily_repeat_count = int(conf_modify.query(job_session, 'daily_repeat_count'))
        if today_total_run_number > daily_repeat_count + (3 - 1):
            conf_modify.put(job_tag=job_session, key="is_retry_count_over", value="true")
            utils_logger.log("此任务今日已重试足够多的次数，放弃吧！！！")
            return
        else:
            conf_modify.put(job_tag=job_session, key="is_retry_count_over", value="false")
        # 实例化job类
        mod_str, _sep, class_str = job_path.rpartition('.')
        __import__(mod_str)
        module_clz = getattr(sys.modules[mod_str], class_str)
        cls_obj = module_clz()
        cls_obj.register_config({"job_session": job_session, "android_device": device})
        # 检查任务对应的设备类型是否匹配
        support_device_types = cls_obj.get_support_device_types_with_task()
        if support_device_types is None or device_type in support_device_types:
            # 若没有给定设备类型或者设备类型在支持列表中，均认为设配类型匹配
            utils_logger.log("允许执行[device_type]")
            conf_modify.put(job_tag=job_session, key="is_device_type_support", value="true")
        else:
            utils_logger.log("任务与设备类型不匹配，直接结束任务")
            conf_modify.put(job_tag=job_session, key="is_device_type_support", value="false")
            return
            # 判断执行周期条件是否满足，比如早上打卡必须是在6~8点
        cur_time = int(utils_common.get_shanghai_time('%H%M'))
        if cls_obj.is_time_support(curent_time=cur_time) is False:
            utils_logger.log("---> 不再执行时间周期内:" + class_str)
            return
            # 判断依赖环境是否满足:不包含设备信息
        dependence_tasks = cls_obj.get_dependence_task()
        if dependence_tasks is not None and check_task_all_finish(device_tag, job_path, dependence_tasks) is False:
            utils_logger.log("---> 依赖项未完成，放弃此次任务")
            return
            # 执行任务
        if cls_obj.run_task() is True:
            cls_obj.notify_job_success()
        # 写入该任务的执行次数，用于对比执行次数与执行成功次数的比例
        today_date = int(utils_common.get_shanghai_time("%Y%m%d"))
        conf_modify.put(job_tag=job_session, key="last_exec_date", value=today_date)
        conf_modify.put(job_tag=job_session, key="today_total_run_number", value=today_total_run_number + 1)
        # 环境清理
        cls_obj.release_after_task()
    except Exception as exception:
        utils_logger.log(traceback.format_exc())
        except_name = exception.__class__.__name__
        utils_logger.log("################################:", except_name)
        email_send.wrapper_send_email(title=u'异常信息[' + except_name + "]",
                                      content="反射调用脚本错误:" + job_path + "\n" + traceback.format_exc())


def check_task_all_finish(device_tag, root_job_path, dependence_task_list):
    """检查任务是否执行完"""
    utils_logger.log("--->[check_task_all_finish]:", dependence_task_list)
    # 若所有的依赖任务的失败原因一致，则该任务也要保证状态一致
    is_device_type_support_dependences_list = []
    is_app_installed_dependences_list = []
    is_all_finish = True
    for task in dependence_task_list:
        job_session = device_tag + "&&" + task
        today_repeat_count_left_with_task = conf_modify.query(job_session, key="today_repeat_count_left")
        is_device_type_support_dependences_list.append(conf_modify.query(job_session, key="is_device_type_support"))
        is_app_installed_dependences_list.append(conf_modify.query(job_session, key="is_app_installed"))
        if today_repeat_count_left_with_task is None:
            #     该任务还没有执行成功过，因此有可能没写入该值
            utils_logger.log("--->[任务从未成功执行过]：", job_session)
            is_all_finish = False
            break
        elif int(today_repeat_count_left_with_task) > 0:
            utils_logger.log("--->[check_task_all_finish]:", job_session)
            is_all_finish = False
            break
    root_job_session = device_tag + "&&" + root_job_path
    if len(list(set(is_device_type_support_dependences_list))) == 1:
        conf_modify.put(root_job_session, key="is_device_type_support",
                        value=is_device_type_support_dependences_list[0])
    return is_all_finish


if __name__ == '__main__':
    run_job()
