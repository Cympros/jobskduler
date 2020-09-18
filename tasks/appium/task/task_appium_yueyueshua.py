# coding=utf-8

import os
import sys
import abc

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

from tasks.appium.task_appium_base import AbsBasicAppiumTask


# from helper import utils_logger


class TaskAppiumYueyueShuaBase(AbsBasicAppiumTask, abc.ABC):
    def __init__(self):
        AbsBasicAppiumTask.__init__(self, "com.weifu.yys", "com.weifu.yys.YStartActivity")


class TaskAppiumYueyueshuaSign(TaskAppiumYueyueShuaBase):
    '月月刷app-签到'

    def run_task(self, _handle_callback):
        if TaskAppiumYueyueShuaBase.run_task(self, _handle_callback) is False:
            return False
        # 左上角'签到'按钮
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.weifu.yys:id/textView1'),
                                  click_mode="click") is not None:
            # 这里'已签到'与'签到领钱'涉及到进入页面动态变更，所以先搜索'已签到'
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('已签到')) is not None:
                utils_logger.log('签到成功')
                return True
            elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('签到领钱'),
                                        click_mode="click") is not None:
                if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('签到成功')) is not None:
                    return True
                else:
                    self.task_scheduler_failed('未找到签到成功的按钮')
                    return False
            else:
                self.task_scheduler_failed('签到失败')
                return False
        else:
            self.task_scheduler_failed('未找到左上角的签到按钮')
            return False
        return False


if __name__ == '__main__':
    import inspect


    def is_class_member(member):
        if inspect.isclass(member) and member.__module__ == __name__:
            # 判断是否是abc.ABC的直接子类
            if abc.ABC not in member.__bases__:
                return True
            else:
                print("goova", member, member.__bases__, issubclass(member, abc.ABC))
        return False


    tasks = [left for left, right in inspect.getmembers(sys.modules[__name__], is_class_member)]
    while True:
        input_info = "------------------------执行任务列表-----------------------\n"
        for index, task_item in enumerate(tasks):
            input_info += str(index) + "：" + task_item + "\n"
        task_index_selected = input(input_info + "请选择需运行任务对应索引(索引下标越界触发程序退出)：")
        if task_index_selected.isdigit() is False:
            utils_logger.log("索引值非数字，请重新输入：", task_index_selected)
            continue
        task_index_selected = int(task_index_selected)
        if task_index_selected >= len(tasks) > 0:
            utils_logger.log("[" + str(task_index_selected) + "]任务索引不存在，退出程序...")
            break
        task_name = tasks[task_index_selected]
        task = eval(task_name + '()')
        task.run_task()
