# coding=utf-8

import os
import sys
import abc

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

from tasks.appium.task_appium_base import AbsBasicAppiumTask
from helper import utils_logger


# apk下载链接：http://sj.qq.com/myapp/detail.htm?apkName=com.sina.weibo

class TaskAppiumSinaWeiboBase(AbsBasicAppiumTask, abc.ABC):
    def __init__(self):
        AbsBasicAppiumTask.__init__(self, "com.sina.weibo", "com.sina.weibo.MainTabActivity")

    def except_case_in_query_ele(self):
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('不了，谢谢'),
                                  click_mode="click",
                                  is_ignore_except_case=True, retry_count=0) is not None:
            # 检测到评分弹窗
            utils_logger.log("检测到评分弹窗")
            return True
        return False


class TaskAppiumSinaWeiboDailyClockOnBase(TaskAppiumSinaWeiboBase):
    """
    微博每日打卡主页面-Base类
    """

    def run_task(self, _handle_callback):
        if TaskAppiumSinaWeiboBase.run_task(self, _handle_callback) is False:
            return False
        if self.wait_activity(driver=self.driver, target=['.MainTabActivity'],
                              retry_count=20) is False:
            self.task_scheduler_failed('进入微博首页失败')
            return False
        if self.query_ele_wrapper(
                "//android.widget.FrameLayout//android.widget.LinearLayout[@resource-id='com.sina.weibo:id/main_radio']//android.view.ViewGroup",
                click_mode='click') is None \
                and self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我'),
                                           click_mode="click") is None:
            self.task_scheduler_failed('not found 个人中心')
            return False
        # if self.query_ele_wrapper("//android.view.View[@content-desc='微博钱包']",click_mode="click") is None:
        #     self.task_scheduler_failed('微博钱包无法进入')
        #     return False
        if self.query_only_point_within_text('^微博钱包$', is_auto_click=True,
                                             cutted_rect=[0, 1, 0.2, 0.7]) is None:
            self.task_scheduler_failed('微博钱包无法进入')
            return False
        # if self.query_ele_wrapper("//android.view.View[@content-desc='早起打卡']",click_mode="click") is None:
        #     self.task_scheduler_failed('早起打卡无法进入')
        #     return False
        # 早起打卡位置可能在四个里面变换
        if self.query_only_point_within_text('^早起打卡$', is_auto_click=True,
                                             cutted_rect=[0, 0.25, 0, 0.5],
                                             retry_count=0) is None \
                and self.query_only_point_within_text('^早起打卡$', is_auto_click=True,
                                                      cutted_rect=[0.25, 0.5, 0, 0.5],
                                                      retry_count=0) is None \
                and self.query_only_point_within_text('^早起打卡$', is_auto_click=True,
                                                      cutted_rect=[0.5, 0.75, 0, 0.5],
                                                      retry_count=0) is None \
                and self.query_only_point_within_text('^早起打卡$', is_auto_click=True,
                                                      cutted_rect=[0.75, 1, 0, 0.5],
                                                      retry_count=0) is None:
            self.task_scheduler_failed("找不到'早起打卡'")
            return False


#
class TaskAppiumSinaWeiboDailyClockOn(TaskAppiumSinaWeiboDailyClockOnBase):
    """
        微博每日打卡
    """

    def task_scheduler_failed(self, message, email_title=u"Error", is_page_source=True,
                              is_scr_shot=True,
                              upload_files=[]):
        TaskAppiumSinaWeiboDailyClockOnBase.task_scheduler_failed(self, message=message,
                                                                  email_title=email_title,
                                                                  is_page_source=is_page_source,
                                                                  is_scr_shot=is_scr_shot,
                                                                  upload_files=upload_files)

    def run_task(self, _handle_callback):
        if TaskAppiumSinaWeiboDailyClockOnBase.run_task(self, _handle_callback) is False:
            return False
        # 判断打卡状态
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('打卡倒计时',
                                                                            view_type='android.widget.Button',
                                                                            is_force_match=False)) is not None \
                or self.query_ele_wrapper(
            self.get_query_str_within_xpath_only_text('打卡倒计时', attribute='content-desc',
                                                      view_type='android.widget.Button',
                                                      is_force_match=False)) is not None:
            utils_logger.log("今日任务已完成")
            return True
        elif self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('支付1元参与挑战', attribute='content-desc',
                                                          view_type='android.widget.Button',
                                                          is_force_match=False),
                click_mode="click") is not None:
            # 包含内容部分：'支付1元参与挑战 挑战成功奖金更多'
            self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('立即支付', attribute='content-desc',
                                                          view_type='android.widget.Button'),
                click_mode="click")
            # 输入支付密码
            if self.query_ele_wrapper(
                    self.get_query_str_within_xpath_only_text('请输入支付密码')) is not None:
                if self.query_ele_wrapper(
                        "//android.widget.LinearLayout//android.widget.TextView[@text='5']",
                        click_mode="click") is not None \
                        and self.query_ele_wrapper(
                    "//android.widget.LinearLayout//android.widget.TextView[@text='2']",
                    click_mode="click") is not None \
                        and self.query_ele_wrapper(
                    "//android.widget.LinearLayout//android.widget.TextView[@text='0']",
                    click_mode="click") is not None \
                        and self.query_ele_wrapper(
                    "//android.widget.LinearLayout//android.widget.TextView[@text='9']",
                    click_mode="click") is not None \
                        and self.query_ele_wrapper(
                    "//android.widget.LinearLayout//android.widget.TextView[@text='4']",
                    click_mode="click") is not None \
                        and self.query_ele_wrapper(
                    "//android.widget.LinearLayout//android.widget.TextView[@text='8']",
                    click_mode="click") is not None:
                    utils_logger.log("write success,sleep to finish")
                    time.sleep(8)
                    return False
                else:
                    utils_logger.log("输入失败")
                    self.task_scheduler_failed('输入失败')
                    return False
            else:
                self.task_scheduler_failed('未检测到密码弹框')
                return False
        elif self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('今日打卡', attribute='content-desc',
                                                          view_type='android.widget.Button'),
                click_mode="click") is not None:
            if self.query_ele_wrapper(
                    self.get_query_str_within_xpath_only_text('继续坚持', attribute='content-desc',
                                                              view_type='android.widget.Button'),
                    click_mode="click") is not None:
                # self.task_scheduler_failed("继续坚持：解析")
                # 不去解析支付 - 检测到继续坚持则认为打卡操作成功
                return False
            else:
                self.task_scheduler_failed("无法解析'继续坚持'")
                return False
        else:
            self.task_scheduler_failed('unknown error')
            return False
        return False

    def is_time_support(self, curent_time=None):
        # 打卡时间：5:00 - 8:00
        is_run_support = True if 500 < curent_time < 800 else False
        utils_logger.log(str(curent_time) + "---> is_run_support(" + str(self.__class__) + "):" + (
            "True" if is_run_support else "False"))
        return is_run_support


class TaskAppiumSinaWeiboReceiverDakaReward(TaskAppiumSinaWeiboDailyClockOnBase):
    """
    领取微博打卡每日奖励
    """

    def run_task(self, _handle_callback):
        if TaskAppiumSinaWeiboDailyClockOnBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(
                "//android.view.View[contains(@content-desc,'其余奖金自获得当日起30天内有效')]") is not None:
            # 进入打卡页面自动弹起领取奖励的弹框的时候
            utils_logger.log("进入'早起打卡'页面like弹出领取奖金成功的弹框")
            self.task_scheduler_failed("--->进入'早起打卡'页面like弹出领取奖金成功的弹框")
            return False
        if self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('我的战绩', view_type='android.view.View',
                                                          attribute='content-desc'),
                click_mode="click") is None \
                and self.query_ele_wrapper(
            self.get_query_str_within_xpath_only_text('我的战绩', view_type='android.view.View'),
            click_mode="click") is None:
            self.task_scheduler_failed('not found 我的战绩')
            return False
        if self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('领取', view_type='android.widget.Button'),
                click_mode="click") is None \
                and self.query_ele_wrapper(
            self.get_query_str_within_xpath_only_text('领取', view_type='android.widget.Button',
                                                      attribute='content-desc'),
            click_mode="click") is None:
            self.task_scheduler_failed("not found '领取'")
            return False
        else:
            # 默认搜索到'领取'按钮并点击，则认为今日打卡奖励已领取，不对点击后的结果做校验(没必要)
            utils_logger.log("发现'领取'按钮并执行点击操作，默认领取成功")
            return True
        # 以下为正则校验点击效果 - 没必要
        # # 仅匹配整数和小数
        # if self.query_only_point_within_text(u'^已领取[0-9]+([.]{1}[0-9]+){0,1}元奖金') is not None:
        #     utils_logger.log("领取微博打卡奖励成功"
        #     return True
        # else:
        #     self.task_scheduler_failed("弹框里无\"已领取0.13元奖金\"类似文案")
        # return False

    def is_time_support(self, curent_time=None):
        # 领取奖励在12点之后
        is_run_support = True if 1200 < curent_time else False
        utils_logger.log(str(curent_time) + "---> is_run_support(" + str(self.__class__) + "):" + (
            "True" if is_run_support else "False"))
        return is_run_support


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
