# coding=utf-8

import os
import sys

job_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.append(job_root_path)

from job.appium.job_appium_base import AppiumBaseJob
from helper import utils_logger


class JobAppiumYueyueShuaBase(AppiumBaseJob):
    def __init__(self):
        AppiumBaseJob.__init__(self, "com.weifu.yys", "com.weifu.yys.YStartActivity")


class JobAppiumYueyueshuaSign(JobAppiumYueyueShuaBase):
    '月月刷app-签到'

    def run_task(self):
        if JobAppiumYueyueShuaBase.run_task(self) is False:
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
                    self.job_scheduler_failed('未找到签到成功的按钮')
                    return False
            else:
                self.job_scheduler_failed('签到失败')
                return False
        else:
            self.job_scheduler_failed('未找到左上角的签到按钮')
            return False
        return False


if __name__ == '__main__':
    tasks = ['JobAppiumYueyueShuaBase', 'JobAppiumYueyueshuaSign']
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
