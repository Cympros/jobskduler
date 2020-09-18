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


class TaskAppiumTaoToutiaoBase(AbsBasicAppiumTask):
    def __init__(self):
        AbsBasicAppiumTask.__init__(self, 'com.ly.taotoutiao', 'com.ly.taotoutiao.view.activity.WelComeActivity')

    def except_case_in_query_ele(self):
        if AbsBasicAppiumTask.except_case_in_query_ele(self) is True:
            return True
        if self.query_ele_wrapper(self.get_query_str_by_viewid("com.ly.taotoutiao:id/img_hd_close"),
                                  is_ignore_except_case=True, click_mode='click') is not None:
            return True
        return False

    def run_task(self, _handle_callback):
        if AbsBasicAppiumTask.run_task(self, _handle_callback) is False:
            return False
        if self.wait_activity(self.driver, ".view.activity.MainActivity") is False:
            self.task_scheduler_failed("未进入淘头条首页")
            return False


class TaskAppiumTaotoutiaoCoreShiduanJiangli(TaskAppiumTaoToutiaoBase):
    def run_task(self, _handle_callback):
        if TaskAppiumTaoToutiaoBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_by_viewid("com.ly.taotoutiao:id/tv_time_countdown"),
                                  click_mode="click") is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("时段奖励")) is not None:
                utils_logger.log("倒计时还未完成")
                return True
            else:
                # 再点击一次
                if self.query_ele_wrapper(self.get_query_str_by_viewid("com.ly.taotoutiao:id/tv_time_countdown"),
                                          click_mode="click") is not None:
                    if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("时段奖励")) is not None:
                        utils_logger.log("二次访问发现获取时段奖励成功")
                        return True
                    else:
                        self.task_scheduler_failed("第二次点击为什么还是没发现时段奖励的提示")
                        return False
                else:
                    self.task_scheduler_failed("第二次次没找到'tv_time_countdown'")
                    return False
        else:
            self.task_scheduler_failed("第一次没找到'tv_time_countdown'")
            return False


class TaskAppiumTaoToutiaoYueDu(TaskAppiumTaoToutiaoBase):
    def run_task(self, _handle_callback):
        if TaskAppiumTaoToutiaoBase.run_task(self, _handle_callback) is False:
            return False
        for_each_size = int(random.randint(1, 15))
        for index in range(for_each_size):
            # 观测是否直接抛异常导致回到桌面
            if utils_appium.get_cur_act(self.driver) == '.Launcher':
                utils_logger.log("运行过程中，软件回到了桌面程序，退出浏览任务")
                return False
            utils_logger.log("开启第(", index, "/", for_each_size, ")次浏览")
            # 循环回到首页
            def_main_activity = '.view.activity.MainActivity'
            if utils_appium.back_to_target_activity(self.driver, def_main_activity) is True:
                try:
                    self.browser_news(def_main_activity)
                except Exception as e:
                    utils_logger.log("TaskAppiumHuiToutiaoYueDu.browser_news caught exception:",
                                     traceback.format_exc())
            else:
                utils_logger.log("不再首页，没办法执行新闻浏览任务")
                break
        return True

    def browser_news(self, main_activity):
        # 最多放6个tab
        module_text = random.choice([u"推荐", u'视频', u'美文', u'故事', u'育儿', u'科技'])
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
        news_activitys = ['.view.activity.NewsDetialTempActivity']
        video_activitys = ['com.lightsky.video.videodetails.ui.activity.VideoDetailsActivity',
                           '.view.activity.VideoDetialActivity']
        other_activitys = ['.view.activity.WebViewActivity', 'com.baidu.mobads.AppActivity',
                           'com.sdk.searchsdk.SearchResultActivity',
                           '.lightbrowser.LightBrowserActivity', '.lightbrowser.LightBrowserActivity',
                           'com.longyun.adsdk.view.AdActivity',
                           'com.uc.browser.InnerUCMobile', 'com.longyun.adsdk.view.AdActivity',
                           'com.qq.e.ads.ADActivity',
                           'com.jd.lib.unification.view.ImageActivity',
                           'com.jd.lib.productdetail.ProductDetailActivity',
                           'com.tencent.mtt.MainActivity', '.PackageInstallerActivity',
                           'com.bytedance.sdk.openadsdk.activity.TTVideoLandingPageActivity',
                           '.schemedispatch.BdBoxSchemeDispatchActivity', 'com.UCMobile.main.UCMobile',
                           'com.jd.lib.jshop.jshop.JshopMainShopActivity',
                           'com.huawei.hwvplayer.service.player.FullscreenActivity']
        for tab_index in range(10):
            if utils_appium.get_cur_act(self.driver) != main_activity:
                utils_logger.log("尝试进入文章时发现不在新闻列表页,直接退出")
                return False
            self.safe_tap_in_point([random.randint(100, 400), random.randint(200, 800)])
            if self.wait_activity(driver=self.driver, target=news_activitys + video_activitys, retry_count=1) is True:
                utils_logger.debug("成功进入某个详情页面")
                break
            else:
                # 进入详情页失败,则先回退至首页
                if utils_appium.back_to_target_activity(self.driver, main_activity) is False:
                    utils_logger.log("等待进入详情页失败,且无法回退至首页,则直接退出浏览")
                    return False
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
