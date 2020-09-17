# coding=utf-8

import os
import sys
import time
import inspect
import threading
import importlib

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../')
sys.path.insert(0, project_root_path)

from helper import utils_logger
from helper import utils_android
from helper import utils_common
from handle_callback import HandleCallback


# 查找指定目录下的所有.py类型的modules文件
def find_all_modules(dir_name):
    from os.path import basename, isfile, join, isdir
    import glob
    # return [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
    whole_py_files = [os.path.realpath(dir_name) + "/" + os.path.basename(f) for f in
                      glob.glob(join(dir_name, "*.py")) if
                      isfile(f) and not f.endswith('__init__.py')]
    for item in os.listdir(dir_name):
        real_path = os.path.join(dir_name, item)
        if not item.endswith('__pycache__') and isdir(real_path):
            whole_py_files += find_all_modules(real_path)
    return whole_py_files


def timestamp_to_date(time_stamp, format_string="%Y%m%d %H:%M:%S"):
    time_array = time.localtime(time_stamp)
    str_date = time.strftime(format_string, time_array)
    return str_date


# 任务对应的状态管理
class TaskState():
    def __init__(self):
        self.next_exec_time = -1

    def update_time(self, taskdesc):
        now_hour = time.localtime().tm_hour
        self.next_exec_time = time.time() + 1000 * utils_common.exponential_decay(1 + now_hour, 24)
        utils_logger.log("更新next_exec_time", taskdesc, timestamp_to_date(self.next_exec_time))

    def __str__(self):
        return 'next_exec_time：%s' % timestamp_to_date(self.next_exec_time)


# 线程调度
class DispatcherThread(threading.Thread):

    def get_task_key(self, task_name):  # 根据'线程id+任务名'唯一标识task_key
        return self.name + "@" + task_name

    def thread_sleep(self):
        time.sleep(15 * 60)  # 参数为秒

    def run(self):
        fail_count = 0
        while True:
            if fail_count >= 3:  # 连续失败3次,则直接休眠30分钟
                utils_logger.log("单个执行周期期间连续失败,尝试系统休眠", self.name)
                self.thread_sleep()
                fail_count = 0
            # 执行任务
            exec_start_time = time.time()
            exec_state = None
            try:
                exec_state = self.exec_single_loop_task()
            except Exception:
                import traceback
                print("exec_single_loop_task catch exception", traceback.format_exc())
            if exec_state is not None and exec_state is True:
                fail_count = 0
            else:
                fail_count += 1
            pass_time = time.time() - exec_start_time  # 单位为秒
            utils_logger.log("pass time is :" + str(pass_time))
            if pass_time < 2 * 60:  # 两分钟以内
                utils_logger.log("单个执行周期执行时间过短,休眠当前线程", self.name)
                self.thread_sleep()

    # 任务遍历的单个执行周期
    def exec_single_loop_task(self):
        exec_result_state = False
        for py_module_path in find_all_modules(project_root_path + "/tasks/appium"):
            (module_dir, tempt) = os.path.split(py_module_path)
            (module_name, extension) = os.path.splitext(tempt)
            if module_name is None \
                    or not module_name.startswith("task_") \
                    or module_name.find("base") > -1:
                continue
            # 动态导入模块
            if not module_dir in sys.path:
                utils_logger.log("> sys.path.append: " + module_dir)
                sys.path.append(module_dir)
            # utils_logger.log("> dynamic import: " + module_name)
            module_dynamic_imported = importlib.import_module(module_name)
            class_results = inspect.getmembers(module_dynamic_imported)
            if class_results is None:
                continue
            for name, obj in class_results:
                if not inspect.isclass(obj):
                    continue
                if name.startswith('AbsBasic') is True:  # Abs开头的基类不参与task执行
                    continue
                # 判断是否到执行时间
                global task_maps
                task_state = task_maps.get(self.get_task_key(name))
                if task_state is None:
                    task_state = TaskState()
                    task_maps[self.get_task_key(name)] = task_state
                now_time = time.time()
                if task_state.next_exec_time > now_time:
                    # utils_logger.log("时间还未到,继续等待", self.get_task_key(name), task_state,
                    #                  "now:" + timestamp_to_date(now_time))
                    continue

                # 反射执行task
                # utils_logger.log("instance to exec task", timestamp_to_date(task_state.next_exec_time),
                #                  "now:" + timestamp_to_date(now_time))
                MyClass = getattr(module_dynamic_imported, name)
                instance = MyClass()
                handle_callback = HandleCallback()
                if instance.run_task(handle_callback) is True:
                    utils_logger.log("成功执行任务", module_dynamic_imported, name)
                    handle_callback.notify_task_success(module_name, name)
                instance.release_after_task()  # 环境清理

                # 添加任务管理
                task_state.update_time(self.get_task_key(name))
                exec_result_state = True  # 仅有一个任务执行成功,也任务整个任务周期是执行成功的
        return exec_result_state


thread_names = []  # 线程集合
task_maps = dict()

# 任务调度器,用于执行task
if __name__ == '__main__':
    # thread_names.append('pc')

    yes = {'yes', 'y'}
    for android_device in utils_android.get_connected_devcies():
        choice = input("确认添加Android线程(yes/y)：" + str(android_device) + "\n")
        if choice in yes:
            utils_logger.log("android_device", android_device)
            thread_names.append(android_device)
        else:
            sys.stdout.write("Please respond with 'yes' or 'no'")
    utils_logger.log("thread_names", thread_names)
    for thread_name in thread_names:
        t = DispatcherThread(name=thread_name)
        t.start()
