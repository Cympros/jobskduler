# coding=utf-8

import os
import sys
import inspect

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../')
sys.path.insert(0, project_root_path)

from helper import utils_logger


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


# 查找指定.py文件中的class信息
def find_class_witthin_module(module_name):
    if not module_dir in sys.path:
        utils_logger.log("> sys.path.append: " + module_dir)
        sys.path.append(module_dir)
    utils_logger.log("> dynamic import: " + module_name)
    import importlib
    return inspect.getmembers(importlib.import_module(module_name))


# 任务调度器,用于执行task
if __name__ == '__main__':
    for py_module_path in find_all_modules(project_root_path + "/tasks/appium"):
        (module_dir, tempt) = os.path.split(py_module_path)
        (module_name, extension) = os.path.splitext(tempt)
        if module_name is None \
                or not module_name.startswith("task_") \
                or module_name.find("base") > -1:
            continue
        class_results = find_class_witthin_module(module_name=module_name)
        if class_results is None:
            continue
        for name, obj in class_results:
            if not inspect.isclass(obj):
                continue
            if name.startswith('AbsBasic') is True:  # Abs开头的基类不参与task执行
                continue
            utils_logger.log(module_name, name)
            continue  # for debug
            MyClass = getattr(my_module, name)
            instance = MyClass()
            if instance.run_task() is True:
                instance.notify_job_success()
            instance.release_after_task()  # 环境清理