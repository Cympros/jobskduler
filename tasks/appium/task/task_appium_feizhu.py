# coding=utf-8

import os
import sys
import abc

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

from tasks.appium.task_appium_base import AbsBasicAppiumTask
from tasks.appium import utils_appium
# from helper import utils_logger
from helper import utils_yaml


# from config import envs


class TaskAppiumFeizhu(AbsBasicAppiumTask):
    def __init__(self):
        AbsBasicAppiumTask.__init__(self, "com.taobao.trip", "com.alipay.mobile.quinox.LauncherActivity")

    def run_task(self, _handle_callback):
        if AbsBasicAppiumTask.run_task(self, _handle_callback) is False:
            return False
        wait_status = self.wait_activity(self.driver, ".home.HomeActivity")
        if not wait_status:
            self.task_scheduler_failed(message='not in .home.HomeActivity')
            return False

        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("领里程"), click_mode="click") is None:
            # 新版做兼容处理
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("今日已签")) is not None:
                return True
            elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(text='里程', is_force_match=False),
                                        click_mode="click") is not None \
                    or self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("马上签到"),
                                              click_mode="click") is not None:
                # '首页'是"+2里程"类似文案
                if self.query_only_point_within_text(search_text=r'^签到\+.里程$', is_auto_click=True) is not None:
                    # 匹配：   签到\+.里程  --->  签到+2里程
                    return False
                else:
                    self.task_scheduler_failed('未找到\"签到\+.里程\"')
                    return False
            else:
                self.task_scheduler_failed("not fount 新版签到入口")
                return False
        else:
            # 判断是否是签到页面
            sign_immediately_element = self.query_ele_wrapper(self.get_query_str_by_desc("立即签到"), click_mode="click")
            if sign_immediately_element is not None:
                return True
            else:
                utils_logger.log("##############未找到立即签到，执行搜素偶已签到逻辑")
                # find "已签到"字符之前先执行下"是否今日还没有签到"的逻辑判断
                if self.query_ele_wrapper(self.get_query_str_by_desc("已签到")) is not None:
                    return True
                else:
                    self.task_scheduler_failed("caught unknown exception when sign in feizhu")
            return False

    def except_case_in_query_ele(self):
        if AbsBasicAppiumTask.except_case_in_query_ele(self) is True:
            return True
        # 用户还没有登录
        cur_act = utils_appium.get_cur_act(self.driver)
        if cur_act == 'com.ali.user.mobile.login.ui.UserLoginActivity':
            # 校验账号密码
            account = utils_yaml.load_yaml(envs.get_yaml_path()).get('feizu_account')
            pwd = utils_yaml.load_yaml(envs.get_yaml_path()).get('feizu_password')
            if account is None or pwd is None:
                self.self.task_scheduler_failed("请设置飞猪账号&密钥")
                return False

            ele_name = self.query_ele_wrapper(self.get_query_str_by_desc('账户名输入框'), is_ignore_except_case=True)
            if ele_name is not None:
                ele_name.send_keys(str(account))
            ele_pwd = self.query_ele_wrapper(self.get_query_str_by_desc('密码输入框'), is_ignore_except_case=True)
            if ele_pwd is not None:
                ele_pwd.send_keys(str(pwd))
            if self.query_ele_wrapper(self.get_query_str_by_viewid('com.taobao.trip:id/loginButton'),
                                      click_mode="click", is_ignore_except_case=True) is not None:
                return True
            else:
                self.task_scheduler_failed("search element by get_query_str_by_viewid for loginButton failed")
        elif self.query_ele_wrapper(self.get_query_str_by_viewid('com.taobao.trip:id/update_contentDialog'),
                                    is_ignore_except_case=True, retry_count=0) is not None:
            if self.query_ele_wrapper(self.get_query_str_by_viewid('com.taobao.trip:id/update_button_cancel'),
                                      click_mode="click", is_ignore_except_case=True) is not None:
                utils_logger.log('---> 检测到更新弹框，但未搜索到取消按钮')
                return True
            else:
                self.task_scheduler_failed("搜索更新弹框的'取消'按钮失败")
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
