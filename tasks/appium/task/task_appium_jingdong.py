# coding=utf-8
import os
import re
import sys
import time
import random

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

from tasks.appium.task_appium_base import BasicAppiumTask
from tasks.appium import utils_appium
from helper import utils_logger


class TaskAppiumJingdong(BasicAppiumTask):
    def __init__(self):
        BasicAppiumTask.__init__(self, "com.jingdong.app.mall", "com.jingdong.app.mall.main.MainActivity")

    def except_case_in_query_ele(self):
        if BasicAppiumTask.except_case_in_query_ele(self) is True:
            return True
        # 关闭全屏模式下左右可滑动的
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.jingdong.app.mall:id/c5w'), click_mode='click',
                                  rect_scale_check_element_region=[0.7, 1, 0, 0.3], is_ignore_except_case=True,
                                  retry_count=0) is not None:
            # if self.query_ele_wrapper('//android.widget.FrameLayout//android.widget.FrameLayout//android.widget.ImageView',click_mode='click',rect_scale_check_element_region=[0.7,1,0,0.3],is_ignore_except_case=True) is not None:
            utils_logger.log("关闭全屏弹框")
            return True
        return False

    def run_task(self):
        return BasicAppiumTask.run_task(self)


# 领京豆页面
class TaskAppiumJDEarnJingDou(TaskAppiumJingdong):

    def except_case_in_query_ele(self):
        if TaskAppiumJingdong.except_case_in_query_ele(self) is True:
            return True
        # '种豆得豆'模块:检索坐标大概在横向居中，竖向在页面下半部分的关闭按钮
        # 注意xpath下支持索引搜索，类似多胞胎兄弟，可通过排行定位，以下表示"FrameLayout/ViewGroup/ViewGroup/ViewGroup"中选择类型是ViewGroup子元素的第二个元素
        if self.query_ele_wrapper(
                "//android.widget.FrameLayout//android.widget.FrameLayout//android.view.ViewGroup//android.view.ViewGroup//android.view.ViewGroup//android.view.ViewGroup//android.widget.ImageView[@instance='23']",
                click_mode='click', rect_scale_check_element_region=[0.4, 0.6, 0.5, 1],
                is_ignore_except_case=True) is not None:
            return True
        return False

    def __enter_earn_jd_pg_within_main(self):
        "从'主页'进入领京豆页面"
        utils_logger.log('---> __enter_earn_jd_pg_within_main')
        if self.query_ele_wrapper(self.get_query_str_by_desc('首页'), click_mode="click") is None:
            utils_logger.log("get_query_str_by_desc('首页') failed")
            return False
        # '领劵'与'领京豆'位置可能变更，因此添加延时
        if self.query_ele_wrapper("//android.widget.TextView[@text='领京豆']", click_mode="click",
                                  time_wait_page_completely_resumed=10) is None:
            utils_logger.log("get_xpath_only_text failed with 领京豆")
            return False
        else:
            return True

    def run_task(self):
        if TaskAppiumJingdong.run_task(self) is False:
            return False
        status = self.wait_activity(self.driver, '.MainFrameActivity')
        if not status:
            self.task_scheduler_failed("wait_activity_with_status failed with '.MainFrameActivity'")
            return False
        if self.__enter_earn_jd_pg_within_main() is True:
            if self.wait_activity(driver=self.driver, target=['com.jd.lib.enjoybuy.EnjoyBuyMainActivity',
                                                              'com.jingdong.common.jdreactFramework.activities.JDReactNativeCommonActivity',
                                                              '.WebActivity']) is True:
                utils_logger.log("校验页面是在领京豆页面")
                return True
            else:
                self.task_scheduler_failed("not in 领京豆页面 by check activity")
                return False
        else:
            self.task_scheduler_failed("未找到'领京豆'的入口")
            return False


# task:正常签到程序
class TaskAppiumJDSignNormal(TaskAppiumJDEarnJingDou):
    def run_task(self):
        if TaskAppiumJDEarnJingDou.run_task(self) is False:
            return False
        # 点击签到按钮
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('已连续签到'), click_mode="click") is None \
                and self.query_ele_wrapper(self.get_query_str_by_desc('已连续签到'), click_mode="click") is None \
                and self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('签到领京豆'),
                                           click_mode="click") is None:
            self.task_scheduler_failed(message="无法找到签到相关的按钮")
            return False

        # 通过辅助元素定位  --->  1.签到日历(十月)  2.'查看更多活动'
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('签到日历', is_force_match=False)) is not None:
            return True
        else:
            self.task_scheduler_failed("签到失败")
            return False


# task:京东签到后补充领取的弹框处理
class TaskAppiumJdSignAdditional(TaskAppiumJDSignNormal):
    def run_task(self):
        if TaskAppiumJDSignNormal.run_task(self) is False:
            utils_logger.log("run_task for TaskAppiumJdSignAdditional failed")
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('今日已翻1张牌')) \
                or self.query_ele_wrapper(
            self.get_query_str_within_xpath_only_text("叫小伙伴一起玩")) is not None:  # 连续15日签到的情况
            return True
        else:
            # 搜索可以点击的控件
            index = random.randint(1, 6)  # 产生0~5的随机数索引
            ele_xpath = '//android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[' \
                        + str(index * 2 + 1) + ']'
            utils_logger.log(ele_xpath)
            if self.query_ele_wrapper(ele_xpath, click_mode="click"):
                if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('收入囊中'),
                                          click_mode="click") is not None \
                        or self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我知道了'),
                                                  click_mode="click") is not None:
                    self.task_scheduler_failed("xpath点击下标索引：" + str(index))
                    return True
                else:
                    self.task_scheduler_failed("not found '收入囊中' or '我知道了'")
                    return False
            else:
                # 默认失败
                self.task_scheduler_failed("not found view to click with ele_xpath with index:" + str(index))
                return False


# task:进店领豆
class TaskAppiumJDEnterShopGotJD(TaskAppiumJDEarnJingDou):
    def run_task(self):
        if TaskAppiumJDEarnJingDou.run_task(self) is False:
            return False
        # 可能会进入'换流量'页面，因此添加延时
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('进店领豆'), click_mode="click",
                                  time_wait_page_completely_resumed=10) is None:
            self.task_scheduler_failed("进入任务集市失败")
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('去完成'), click_mode="click") is None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('本期任务已被抢光，明天再来吧')) is not None:
                # 任务被抢光
                utils_logger.log("任务被枪光，标记任务完成")
                return True
            # 检查是否有进店逛逛
            elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('进店逛逛')) is not None:
                # 此时'去完成'已没有，但是'进店逛逛'可以找到，说明今日份已全部领取完
                return True
            elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('即将开始')) is not None:
                utils_logger.log("活动还未开始")
                # 此时不发送邮件说明
                return False
            else:
                self.task_scheduler_failed("进入的界面不正确")
                return False
        else:
            # 关注店铺领取奖励 & 判断当前界面
            if self.query_ele_wrapper(self.get_query_str_by_viewid('com.jd.lib.jshop:id/view_jshop_gifts_take_button'),
                                      click_mode="click") is not None \
                    or utils_appium.get_cur_act(self.driver,
                                                delay_time=3) == 'com.jd.lib.jshop.jshop.JshopMainShopActivity':
                return True
            else:
                self.task_scheduler_failed("未进入店铺")
                return False


# task:转福利
class TaskAppiumJDZhuanFuli(TaskAppiumJDEarnJingDou):
    def run_task(self):
        if TaskAppiumJDEarnJingDou.run_task(self) is False:
            return False
        # 可能会进入'购物返豆'页面，故而添加延时
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('转福利'), click_mode="click",
                                  time_wait_page_completely_resumed=10) is None:
            self.task_scheduler_failed("进入转福利页面失败")
            return False
        only_point = self.query_only_point_within_text('^您还有.次抽奖机会(!$|$)|^今日还可以抽.次哦$|^可以抽.次哦$')
        if only_point is not None:
            # 判断剩余次数是否大于0
            find_words = only_point['words']
            find_all_result = re.findall(r"^您还有(\d)次抽奖机会(!$|$)|^今日还可以抽(\d)次哦$|^可以抽(\d)次哦$", str(find_words))
            utils_logger.log("##############################[find_all_result]:", find_words, find_all_result)
            if find_all_result is not None and len(find_all_result) > 0:
                value_a = [chance for chance in find_all_result[0] if chance != ""]
                utils_logger.log("#####################[value_a]:", find_words, value_a)
                if len(value_a) == 1:
                    if int(value_a[0]) <= 0:
                        utils_logger.log("检测剩余次数不足，认为今日任务已完成")
                        return True

        # 如果检测不到'您还有 0 次抽奖机会'可能是该部分内容根本就没有展示，因此不管三七二十一，抽奖了再说
        if self.query_only_point_within_text(r'^抽奖$|^GO$', is_auto_click=True) is not None:
            utils_logger.log("等待抽奖完成")
            time.sleep(8)  # 等待抽奖完成
        else:
            self.task_scheduler_failed('未找到\'开始抽奖\'按钮')
            return False


class TaskAppiumJDUserMeiriFuli(TaskAppiumJDEarnJingDou):
    """task：京东用户每日福利"""

    def run_task(self):
        if TaskAppiumJDEarnJingDou.run_task(self) is False:
            return False
        if self.query_only_point_within_text('^京东用户每日福利$', is_auto_click=True, cutted_rect=[0.65, 1, 0, 1]) is None:
            self.task_scheduler_failed("进入转福利页面失败")
            return False
        else:
            if self.query_only_point_within_text('^今日已抽奖$') is not None:
                return True
            elif self.query_only_point_within_text('^今天1次机会$', is_auto_click=True) is not None:
                utils_logger.log("找到\"今天1次机会\",sleep for 等待每日抽奖")
                time.sleep(8)  # 等待每日抽奖
                return False
            else:
                self.task_scheduler_failed('TaskAppiumJDUserMeiriFuli failed')
                return False


class TaskAppiumJDUserMeiriFuliAddition(TaskAppiumJDUserMeiriFuli):
    """京东用户每日福利-每日签到"""

    def run_task(self):
        if TaskAppiumJDUserMeiriFuli.run_task(self) is False:
            return False
        if self.query_only_point_within_text(search_text='^签到领取$', is_auto_click=True,
                                             cutted_rect=[0, 1, 0.4, 1]) is not None:
            if self.query_point_size_within_text(r'^该小时奖品已发放完*') > 0:
                utils_logger.log("该小时没获得奖励")
                return False
            else:
                self.task_scheduler_failed('签到领取后的效果')
                return False
        elif self.query_point_size_within_text('^已签到领取$', cutted_rect=[0, 1, 0.4, 1]) > 0:
            return True
        else:
            self.task_scheduler_failed('未找到\"签到领取\"相关按钮')
            return False


class TaskAppiumJDVoucherCenter(TaskAppiumJingdong):
    """首页领卷中心内部的签到"""

    def run_task(self):
        if TaskAppiumJingdong.run_task(self) is False:
            return False
        status = self.wait_activity(self.driver, '.MainFrameActivity')
        if not status:
            self.task_scheduler_failed("wait_activity_with_status failed with '.MainFrameActivity'")
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("领券"), click_mode="click") is None:
            self.task_scheduler_failed("get_xpath_only_text failed with 领券")
            return False
        else:
            # 检查标题是否是"领京豆"
            if utils_appium.get_cur_act(driver=self.driver, delay_time=3).startswith(
                    'com.jd.lib.coupon.lib.CouponCenterActivity'):
                # utils_logger.log("成功进入标题'领券中心'界面"
                if self.query_ele_wrapper(
                        "//android.widget.TextView[@text='等待开抢' and @resource-id='com.jd.lib.coupon:id/sign_get_button']") is not None:
                    # 3天签到已满足，不用点击
                    utils_logger.log("三天签到已满足，今日不用再签到")
                    return True
                elif self.query_ele_wrapper(self.get_query_str_by_viewid('com.jd.lib.coupon:id/sign_get_button'),
                                            click_mode="click") is not None:
                    if self.query_ele_wrapper("//android.widget.TextView[contains(@text,'坐等开奖']") is not None \
                            or self.query_point_size_within_text(r'^(已签\d天($|(,|，)坐等开奖$)|^签到领3元无门槛*)') > 0:
                        return True
                    else:
                        self.task_scheduler_failed('未检测到中心弹框\"已签到n天\"部分内容')
                        return False
                else:
                    self.task_scheduler_failed(message='未找到指定元素')
                    return False
            else:
                self.task_scheduler_failed("未进入'领券中心'界面")
                return False


class TaskAppiumJDSignDoubleSign(TaskAppiumJDEarnJingDou):
    """京豆双签逻辑"""

    def get_dependence_task(self):
        return ["task_appium_jingdong.TaskAppiumJDSignNormal", "task_appium_jdjr.TaskAppiumJDJRSign"]

    def run_task(self):
        if TaskAppiumJDEarnJingDou.run_task(self) is False:
            return False

        # 双签按钮
        if self.query_only_match_part_with_click('jingdong_double_sign_enterence.png',
                                                 part_rect_scale=[0.82, 0.98, 0.47, 0.568], is_auto_click=True) is None \
                and self.query_only_point_within_text(r'^双签京豆$', is_auto_click=True, retry_count=0) is None:
            utils_logger.log("找不到领取双签入口")
            self.task_scheduler_failed('找不到领取双签入口')
            return False

        # 查看表示是否是"双签领奖励"
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('双签领奖励')) is None:
            self.task_scheduler_failed("未进入双签界面")
            return False

        # 此时在'双签领奖励'界面
        if self.query_only_point_within_text('^点击查看礼包$') is not None:
            return True
        elif self.query_only_point_within_text(search_text='^立即领取$', is_auto_click=True) is not None:
            # 去签到的两种情况：1.进入页面就弹出弹框，弹框中包含'恭喜你获得双签礼包'  2.三栏中双签部分是'立即领取'
            return False
        elif self.query_ele_wrapper(self.get_query_str_by_desc('去签到')) is not None \
                or self.query_point_size_within_text('^去签到$') > 0:
            utils_logger.log("双签条件还没有满足")
            return False
        else:
            self.task_scheduler_failed("双签操作失败")
            return False


if __name__ == '__main__':
    import inspect

    tasks = [left for left, right in inspect.getmembers(sys.modules[__name__], inspect.isclass)
             if not left.startswith('Basic')]
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
