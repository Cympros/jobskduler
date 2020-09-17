# coding=utf-8
"""惠头条"""
import os
import sys
import random
import time
import traceback

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

from tasks.appium.task_appium_base import AbsBasicAppiumTask
from tasks.appium import utils_appium


# from helper import utils_logger


class TaskAppiumHuiToutiaoBase(AbsBasicAppiumTask):
    def __init__(self):
        AbsBasicAppiumTask.__init__(self, 'com.cashtoutiao', 'com.cashtoutiao.common.ui.SplashActivity')

    def except_case_in_query_ele(self):
        if AbsBasicAppiumTask.except_case_in_query_ele(self) is True:
            return True
        if self.query_ele_wrapper(
                "//android.widget.LinearLayout//android.widget.FrameLayout//android.widget.RelativeLayout"
                + "//android.widget.LinearLayout//android.widget.ImageView[@resource-id='com.cashtoutiao:id/img_close']",
                click_mode="click", is_ignore_except_case=True) is True:
            utils_logger.log("检测到弹框部分，搜索弹框右上角的关闭按钮")
            return True
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("安全升级"),
                                    is_ignore_except_case=True) is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("以后再说"), click_mode='click',
                                      is_ignore_except_case=True) is None:
                self.task_scheduler_failed("检测到'安全升级'按钮,但没办法'关闭更新'弹框")
                return False
            else:
                return True
        # 检测到信息流页面直接弹出"您当前处于WIFI网络环境下，可安全下载，不消耗您的数据流量。"的"下载提示"弹框
        elif self.query_ele_wrapper(self.get_query_str_by_viewid("com.cashtoutiao:id/dialog_custom_style_double_btns"),
                                    is_ignore_except_case=True) is not None:
            if self.query_ele_wrapper(self.get_query_str_by_viewid("com.cashtoutiao:id/confirm_cancel"),
                                      click_mode="click", is_ignore_except_case=True) is not None:
                return True
            else:
                self.task_scheduler_failed("检测到'下载提示弹框'，但无法关闭")
                return False
        return False

    def run_task(self, _handle_callback):
        if AbsBasicAppiumTask.run_task(self, _handle_callback) is False:
            return False
        if self.wait_activity(self.driver, "com.cashtoutiao.account.ui.main.MainTabActivity") is False:
            self.task_scheduler_failed("未进入惠头条首页")
            return False


class TaskAppiumHuitoutiaoCoreShiduanJiangli(TaskAppiumHuiToutiaoBase):
    def run_task(self, _handle_callback):
        if TaskAppiumHuiToutiaoBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_by_viewid("com.cashtoutiao:id/count_down_tv"),
                                  click_mode="click") is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("时段奖励领取成功"),
                                      click_mode="click") is not None:
                utils_logger.log("时段奖励领取成功")
                return True
            elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("什么是时段奖励"),
                                        click_mode="click") is not None:
                utils_logger.log("正在倒计时当中")
                return True
            else:
                # 没有弹框提示
                # self.task_scheduler_failed("没有时段奖励领取成功提示")
                return False
        else:
            self.task_scheduler_failed("没找到时段奖励")
            return False


class TaskAppiumHuiToutiaoYueDu(TaskAppiumHuiToutiaoBase):
    def run_task(self, _handle_callback):
        if TaskAppiumHuiToutiaoBase.run_task(self, _handle_callback) is False:
            return False
        for_each_size = int(random.randint(1, 15))
        for index in range(for_each_size):
            # 观测是否直接抛异常导致回到桌面
            if utils_appium.get_cur_act(self.driver) == '.Launcher':
                utils_logger.log("运行过程中，软件回到了桌面程序，退出浏览任务")
                return False
            utils_logger.log("开启第(", index, "/", for_each_size, ")次浏览")
            # 循环回到首页
            def_main_activity = '.account.ui.main.MainTabActivity'
            if utils_appium.back_to_target_activity(self.driver, def_main_activity) is True:
                try:
                    self.browser_news(def_main_activity)
                except Exception as e:
                    utils_logger.log("TaskAppiumHuiToutiaoYueDu.browser_news caught exception:",
                                     traceback.format_exc())
            else:
                utils_logger.log("不再首页，没办法执行新闻浏览任务")
                break

    def browser_news(self, main_activity):
        # 至多7个tab
        module_text = random.choice([u"关注", u'头条', u'娱乐', u'奇趣', u'美食'])
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(module_text), click_mode="click",
                                  retry_count=0) is None:
            self.task_scheduler_failed('找不到' + module_text + '板块')
            return False
        is_view_inflated, scr_shots = self.wait_view_layout_finish(True)
        if is_view_inflated is False:
            self.task_scheduler_failed('页面还未绘制完成，please check')
            return False
        # 搜索应该阅读的文章
        scroll_size = int(random.randint(0, 10))
        utils_logger.log("页面滚动次数：", scroll_size)
        for index in range(scroll_size):
            # 滑动以选择文章开启阅读任务
            self.safe_touch_action(tab_interval=[float(random.uniform(0.65, 0.35)), 0.35])
        # 随便点击，选择指定文章开始读取
        news_activitys = ['.news.ui.NewsDetailActivity']
        video_activitys = ['.alivideodetail.AliVideoDetailActivity']
        other_activitys = ['com.bdtt.sdk.wmsdk.activity.TTLandingPageActivity', '.common.ui.CustomBrowserWithoutX5',
                           'com.bytedance.sdk.openadsdk.activity.TTLandingPageActivity', '.HTouTiaoActivity',
                           'com.jd.lib.unification.view.ImageActivity',
                           '.WebActivity', 'com.tencent.mtt.MainActivity', 'com.qq.e.ads.ADActivity',
                           '.news.ui.ImageWatcherActivity',
                           'com.ak.torch.shell.landingpage.TorchActivity', '.lightbrowser.LightBrowserActivity',
                           'com.baidu.mobads.AppActivity', 'com.huawei.hwvplayer.service.player.FullscreenActivity',
                           'com.jingdong.common.babel.view.activity.BabelActivity', '.accounts.SyncSettingsActivity']
        for tab_index in range(10):
            self.safe_tap_in_point([random.randint(100, 400), random.randint(200, 800)])
            utils_logger.log("等待进入新闻详情界面[", tab_index, "]：", utils_appium.get_cur_act(self.driver))
            # wait_activity有针对异常情况的处理，因此弃用'utils_appium.get_cur_act'方式
            if self.wait_activity(driver=self.driver, target=news_activitys + video_activitys + other_activitys,
                                  retry_count=1) is True:
                utils_logger.log("成功进入某个详情页面")
                break
        # 判断是否在详情页面
        cur_activity = utils_appium.get_cur_act(self.driver)
        if cur_activity == main_activity:
            self.task_scheduler_failed('why 还在首页')
            return False
        # 根据页面调用指定阅读策略
        utils_logger.log("cur_activity:", cur_activity)
        if cur_activity in news_activitys:
            # 开始模拟阅读
            time_to_foreach = random.randint(5, 10)  # 5~10s，因为每30秒就可以获得10积分的奖励
            period = 0.2  # 每次浏览间隔，单位：秒
            for index in range(int(float(time_to_foreach) / period)):
                if utils_common.random_boolean_true(0.65) is True:
                    tab_interval = [0.65, 0.35]
                else:
                    tab_interval = [0.25, 0.75]
                utils_logger.log("[", time_to_foreach, "] for tab_interval[", tab_interval, "] with index:", index)
                if self.safe_touch_action(tab_interval=tab_interval, duration=int(float(period * 1000))) is False:
                    utils_logger.log("----> safe_touch_action caught exception")
            return True
        elif cur_activity in video_activitys:
            utils_logger.log("等待视频播放完成：45")
            time.sleep(random.randint(25, 90))  # 休眠45秒
            return True
        elif cur_activity in other_activitys:
            utils_logger.log("进入非指定详情页面，放弃此次浏览")
            return False
        else:
            self.task_scheduler_failed(message='未知页面:' + cur_activity, email_title="UnknownPage")
            return False


if __name__ == '__main__':
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
