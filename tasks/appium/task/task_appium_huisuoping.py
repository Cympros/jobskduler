# coding=utf-8

import os
import sys

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

from tasks.appium.task_appium_base import AbsBasicAppiumTask


# from helper import utils_logger


class TaskAppiumHuiSuoPingBase(AbsBasicAppiumTask):
    def __init__(self):
        AbsBasicAppiumTask.__init__(self)

    def except_case_in_query_ele(self):
        if AbsBasicAppiumTask.except_case_in_query_ele(self) is True:
            return True
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("友情提醒"), is_ignore_except_case=True,
                                    retry_count=0) is not None:
            if self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/confirm_cancel'),
                                      is_ignore_except_case=True, click_mode="click", retry_count=0) is not None:
                return True
            else:
                self.task_scheduler_failed('why not found com.huaqian:id/confirm_cancel')
                return False
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('立即更新'), is_ignore_except_case=True,
                                    retry_count=0) is not None:
            utils_logger.log("检测到版本更新")
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('以后再说'), click_mode='click',
                                      is_ignore_except_case=True, retry_count=0) is not None:
                return True
            else:
                self.task_scheduler_failed('关闭更新弹框失败')
        return False

    def task_scheduler_failed(self, message, email_title=u'异常信息', is_page_source=True, is_scr_shot=True):
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('网络出错了，请待会再试吧', is_force_match=False),
                                  is_ignore_except_case=True, retry_count=0) is not None:
            utils_logger.log("TaskAppiumHuiSuoPingBase.task_scheduler_failed:网络出错，调整邮件提醒类别")
            AbsBasicAppiumTask.task_scheduler_failed(self, email_title='网络异常', message=message,
                                                     is_page_source=is_page_source,
                                                     is_scr_shot=is_scr_shot)
        else:
            AbsBasicAppiumTask.task_scheduler_failed(self, email_title=email_title, message=message,
                                                     is_page_source=is_page_source, is_scr_shot=is_scr_shot)


class TaskAppiumHuiSuoPingHourCredit(TaskAppiumHuiSuoPingBase):
    '每小时的红包'

    def run_task(self, _handle_callback):
        if TaskAppiumHuiSuoPingBase.run_task(self, _handle_callback) is False:
            return False
        if self.wait_activity(driver=self.driver, target='.account.ui.main.MainTabActivity', retry_count=20) is False:
            self.task_scheduler_failed('not in .account.ui.main.MainTabActivity')
            return False
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/rlayout_menu')) is None:
            # 顶部右边是'邀请好友'的顶部titlebar部分
            self.task_scheduler_failed("没找到顶部的'titlebar'部分内容")
            return False
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/hour_credit'),
                                  click_mode="click") is not None \
                or self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/hour_credit_container'),
                                          click_mode="click") is not None:
            return True
        elif self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/redbag_count_down')) is not None:
            utils_logger.log("TaskAppiumHuiSuoPingHourCredit : still in count_down")
            return True
        else:
            self.task_scheduler_failed("query failed for viewid of com.huaqian:id/hour_credit")
            return False


class TaskAppiumHuiSuoPingDailySign(TaskAppiumHuiSuoPingBase):
    '每日签到'

    def run_task(self, _handle_callback):
        if TaskAppiumHuiSuoPingBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(text="每日签到"), click_mode="position",
                                  rect_scale_check_element_region=[0.5, 0.75, 0, 1]) is not None:
            if self.query_only_point_within_text(r'^您已签到并领取\d+金币$', is_auto_click=True) is not None:
                return True
            else:
                # 这里没必要通知，直接忽略该异常
                utils_logger.log("task_scheduler_failed:'您已签到并领取\d+金币 not matched'")
                # self.task_scheduler_failed('您已签到并领取\d+金币 not matched')
                return False
        # elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(text='签到中心'),click_mode="click") is not None\
        #         or self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(text="任务中心"),click_mode="click") is not None:
        #     if self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/button_sign'),click_mode="click") is not None:
        #         return True
        #     else:
        #         self.task_scheduler_failed("立即签到按钮未找到")
        #         return False
        else:
            self.task_scheduler_failed("未找到\'每日签到\'入口")
        return False


class TaskAppiumHuiSuoPingMoreMakeMoneyBase(TaskAppiumHuiSuoPingBase):
    """更多赚钱入口基类"""

    def run_task(self, _handle_callback):
        if TaskAppiumHuiSuoPingBase.run_task(self, _handle_callback) is False:
            return False
        if self.wait_activity(self.driver, target=['.account.ui.main.MainTabActivity']) is False:
            self.task_scheduler_failed('why not in 首页')
            return False
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/more_channel_container'),
                                  click_mode='click', time_wait_page_completely_resumed=10) is None \
                and self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('更多赚钱'), click_mode="click",
                                           time_wait_page_completely_resumed=10) is None:
            self.task_scheduler_failed('\"更多赚钱\" 找不到')
            return False
        if self.wait_activity(self.driver, target=['.market.ui.activity.MoreChannelActivity']) is False:
            self.task_scheduler_failed('未进入更多赚钱页面')
            return False
        return True


class TaskAppiumHuiSuoPingDailyClockOn(TaskAppiumHuiSuoPingMoreMakeMoneyBase):
    """
        每日6~8点打卡时间
        1.每天6~8点执行该方法，避免query_only_point_within_text的无效调用
        2.只有按钮是'打卡倒计时'，才认为是当天任务已完成：每天的任务=今日签到成功+明天签到活动报名
        3.6~8点之间打完卡后，会搜索不到'支付1元参与挑战'，因此调整该任务晚执行时间至10点
    """

    def is_time_support(self, curent_time=None):
        is_run_support = True if 600 < curent_time < 1000 else False
        utils_logger.log(str(curent_time) + "---> is_run_support(" + str(self.__class__) + "):" + (
            "True" if is_run_support else "False"))
        return is_run_support

    def task_scheduler_failed(self, message, email_title=u'Error', is_page_source=True, is_scr_shot=True):
        # clockon任务失败影响超级严重，特殊处理
        TaskAppiumHuiSuoPingMoreMakeMoneyBase.task_scheduler_failed(self, message=message, email_title=email_title,
                                                                    is_page_source=is_page_source,
                                                                    is_scr_shot=is_scr_shot)

    def run_task(self, _handle_callback):
        if TaskAppiumHuiSuoPingMoreMakeMoneyBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('早起打卡'), click_mode="click") is None:
            self.task_scheduler_failed('\"早起打卡\"找不到')
            return False
        # TODO：在打卡时间段若已打卡，则按钮会变成空白色
        if self.query_only_point_within_text(search_text=r'^打卡倒计时*') is not None:
            return True
        elif self.query_only_point_within_text('^立即打卡$', is_auto_click=True) is not None:
            if self.query_only_point_within_text('^继续坚持打卡$', is_auto_click=True) is not None:
                return False
            else:
                self.task_scheduler_failed('已打卡，但未搜索到\"打卡成功\"标识')
                return False
        elif self.query_only_point_within_text(search_text='^支付1元参与挑战$', is_auto_click=True) is not None:
            self.task_scheduler_failed('TODO:解析结果')
            return False
        self.task_scheduler_failed(message='---> TaskAppiumHuiSuoPingDailyClockOn failed',
                                   email_title='TaskAppiumHuiSuoPingDailyClockOn.FoundEmptyError')
        return False


class TaskAppiumHuiSuoPingActiveRedPkg(TaskAppiumHuiSuoPingMoreMakeMoneyBase):
    """更多赚钱-活跃红包"""

    def run_task(self, _handle_callback):
        if TaskAppiumHuiSuoPingMoreMakeMoneyBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('活跃红包'), click_mode="click") is None:
            self.task_scheduler_failed('\"活跃红包\"找不到')
            return False
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/open_progress')) is not None:
            # '财神爷'图片
            if self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/image_red'), click_mode="click",
                                      retry_count=0) is not None:
                if self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/image_open_icon'),
                                          click_mode="click", retry_count=0) is not None:
                    # 点击'领取红包'按钮,'领取中'时需要等待5秒
                    time.sleep(5)
                    if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('什么都没抽到～'),
                                              retry_count=0) is not None:
                        utils_logger.log("红包什么都没有抽到")
                        return True
                    elif self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/image_collar'),
                                                click_mode="click", retry_count=0) is not None \
                            or self.query_only_point_within_text('^立即领取$', is_auto_click=True,
                                                                 retry_count=0) is not None:
                        # 注意：不点击按钮是不是也可以领取到奖励，因此没有再深入解析结果的必要
                        utils_logger.log("点击\"立即领取\"按钮领取红包：解析结果...")
                        return True
                    else:
                        self.task_scheduler_failed('打开红包弹框，但发现红包元素无法解析')
                        return False
                elif self.query_ele_wrapper(self.get_query_str_by_viewid('com.huaqian:id/image_red_msg'),
                                            retry_count=0) is not None:
                    # 提示无活跃值用于抽奖:无活跃值时点击财神爷无反应
                    utils_logger.log("提示：无活跃值用于抽奖")
                    return True
                else:
                    self.task_scheduler_failed('why not found image_open_icon/image_red_msg')
                    return False
            else:
                self.task_scheduler_failed('why not found 无法点击')
                return False
        else:
            self.task_scheduler_failed('没找到进度条')
            return False
        return False


class TaskAppiumHuiSuoPingLuckyPan(TaskAppiumHuiSuoPingMoreMakeMoneyBase):
    '幸运转盘'

    def run_task(self, _handle_callback):
        if TaskAppiumHuiSuoPingMoreMakeMoneyBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('幸运转盘'), click_mode="click") is None:
            return False
        # if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('温馨提示')) is not None:
        #     # 此时要求体验60秒以上
        #     if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('继续体验'),
        #                               click_mode="click") is not None:
        #         time.sleep(60 + 15)
        #     else:
        #         self.task_scheduler_failed("检测到温馨提示，但是没检测到继续体验按钮")
        #         return False


if __name__ == "__main__":
    import inspect


    def is_class_member(member):
        return inspect.isclass(member) and member.__module__ == __name__


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
