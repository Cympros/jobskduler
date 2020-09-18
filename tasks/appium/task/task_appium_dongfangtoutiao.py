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
from helper import utils_logger
from helper import utils_android
from helper import utils_common


class TaskAppiumDongFangToutiaoBase(AbsBasicAppiumTask):
    def __init__(self):
        AbsBasicAppiumTask.__init__(self, 'com.songheng.eastnews',
                                    'com.oa.eastfirst.activity.WelcomeActivity')

    def except_case_in_query_ele(self):
        return AbsBasicAppiumTask.except_case_in_query_ele(self)

    def run_task(self, _handle_callback):
        if AbsBasicAppiumTask.run_task(self, _handle_callback) is False:
            return False
        if self.wait_activity(self.driver,
                              "com.songheng.eastfirst.common.view.activity.MainActivity") is False:
            self.task_scheduler_failed("未进入东方头条首页")
            return False


class TaskAppiumDongFangtoutiaoCoreShiduanJiangli(TaskAppiumDongFangToutiaoBase):
    def run_task(self, _handle_callback):
        if TaskAppiumDongFangToutiaoBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("领取"),
                                  click_mode="click") is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("时段奖励领取成功"),
                                      click_mode="click") is not None:
                utils_logger.log("时段奖励领取成功")
                return True
            else:
                self.task_scheduler_failed("没有时段奖励领取成功提示")
                return False
        elif self.query_ele_wrapper(
                "//android.support.v4.view.ViewPager//android.widget.RelativeLayout//android.widget.FrameLayout" \
                + "//android.widget.LinearLayout//android.widget.RelativeLayout//android.widget.LinearLayout"
                + "//android.widget.FrameLayout//android.widget.RelativeLayout//android.widget.LinearLayout"
                + "//android.widget.RelativeLayout//android.widget.RelativeLayout//android.widget.TextView") is not None:
            utils_logger.log("搜索到倒计时按钮")
            return True
        else:
            self.task_scheduler_failed("没找到时段奖励")
            return False


class TaskAppiumDongFangToutiaoYueDu(TaskAppiumDongFangToutiaoBase):
    def run_task(self, _handle_callback):
        if TaskAppiumDongFangToutiaoBase.run_task(self, _handle_callback) is False:
            return False
        for_each_size = int(random.randint(1, 15))
        for index in range(for_each_size):
            # 观测是否直接抛异常导致回到桌面
            if utils_android.get_resumed_activity(self.target_device_name) == '.Launcher':
                utils_logger.log("运行过程中，软件回到了桌面程序，退出浏览任务")
                return False
            utils_logger.log("开启第(" + str(index) + "/" + str(for_each_size) + ")次浏览")
            # 循环回到首页
            def_main_activity = 'com.songheng.eastfirst.common.view.activity.MainActivity'
            if utils_appium.back_to_target_activity(self.driver, def_main_activity) is True:
                try:
                    self.browser_news(def_main_activity)
                except Exception as e:
                    utils_logger.log("browser_news caught exception:", traceback.format_exc())
            else:
                utils_logger.log("不再首页，没办法执行新闻浏览任务")
                break

    def browser_news(self, main_activity):
        # TODO: 不要指定具体的tab
        # module_text = random.choice([u"推荐", u'热点', u'视频', u'社会', u'科技', u'军事', u'国际'])
        # if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(module_text),
        #                           click_mode="click",
        #                           retry_count=0) is None:
        #     self.task_scheduler_failed('找不到' + module_text + '板块')
        #     return False
        is_view_inflated, scr_shots = self.wait_view_layout_finish(True)
        if is_view_inflated is False:
            self.task_scheduler_failed('页面还未绘制完成，please check')
            return False
        # 搜索应该阅读的文章
        scroll_size = int(random.randint(0, 10))
        utils_logger.debug("页面滚动次数：", scroll_size)
        for index in range(scroll_size):
            # 滑动以选择文章开启阅读任务
            self.safe_touch_action(tab_interval=[float(random.uniform(0.65, 0.35)), 0.35])
        # 随便点击，选择指定文章开始读取
        news_activitys = ['com.songheng.eastfirst.business.newsdetail.view.activity.NewsDetailH5Activity',
                          'com.songheng.eastfirst.business.newsdetail.view.activity.NewsDetailHardwareActivity']
        video_activitys = ['.alivideodetail.AliVideoDetailActivity',
                           'com.songheng.eastfirst.business.video.view.activity.VideoDetailActivity']
        other_activitys = ['com.bdtt.sdk.wmsdk.activity.TTLandingPageActivity', '.EastNewActivity',
                           '.lightbrowser.LightBrowserActivity', 'com.tencent.mtt.MainActivity',
                           'com.qq.e.ads.ADActivity', 'com.jd.lib.unification.view.ImageActivity',
                           'com.jd.lib.productdetail.ProductDetailActivity',
                           'com.songheng.eastfirst.business.newsdetail.view.activity.NewsDetailImageGalleryActivity',
                           'com.songheng.eastfirst.common.view.activity.WebViewActivity',
                           'com.uc.browser.InnerUCMobile', '.WebActivity', '.PackageInstallerActivity',
                           'com.bytedance.sdk.openadsdk.activity.TTVideoLandingPageActivity']
        for tab_index in range(10):
            if utils_android.get_resumed_activity(self.target_device_name) != main_activity:
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
                # 回退至首页时,增加随机滚动,避免又点入同一份广告
                self.safe_touch_action(tab_interval=[float(random.uniform(0.65, 0.35)), 0.35])
        # 判断是否在详情页面
        cur_activity = utils_android.get_resumed_activity(self.target_device_name)
        if cur_activity == main_activity:
            utils_logger.log('why 还在首页 cur_activity:' + str(cur_activity) + ",main_activity:" + str(main_activity))
            self.task_scheduler_failed('why 还在首页')
            return False
        # 根据页面调用指定阅读策略
        utils_logger.debug("cur_activity:", cur_activity)
        if cur_activity in news_activitys + video_activitys:
            # 判断是否有进度条
            if self.query_ele_wrapper(
                    '//android.support.v4.widget.SlidingPaneLayout/android.widget.RelativeLayout/android.widget'
                    '.LinearLayout[3]/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget'
                    '.RelativeLayout/android.widget.RelativeLayout/android.view.View',
                    is_ignore_except_case=True, retry_count=0) is None:
                utils_logger.log("详情页无阅读积分进度框,是无效阅读")
                return False

            if cur_activity in news_activitys:
                # 开始模拟阅读
                time_to_foreach = random.randint(5, 10)  # 5~10s，因为每30秒就可以获得10积分的奖励
                period = 0.2  # 每次浏览间隔，单位：秒
                for index in range(int(float(time_to_foreach) / period)):
                    if utils_common.random_boolean_true(0.75) is True:
                        tab_interval = [0.65, 0.35]
                    else:
                        tab_interval = [0.25, 0.75]
                    utils_logger.debug(
                        "[" + str(time_to_foreach) + "] for tab_interval[" + str(tab_interval) + "] with index:" + str(
                            index))
                    if self.safe_touch_action(tab_interval=tab_interval,
                                              duration=int(float(period * 1000))) is False:
                        utils_logger.log("----> safe_touch_action caught exception")
                        return False
                    # 东方头条有可能向下拖动的时候退出详情页,因此添加检测机制
                    if utils_android.get_resumed_activity(self.target_device_name) == main_activity:
                        utils_logger.log("向下拖动太狠,已经退出详情页,结束浏览")
                        return True
                    # 检测是否存在"点击阅读全文"的文案
                    if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("点击阅读全文"), retry_count=0,
                                              click_mode="click", is_ignore_except_case=True) is not None:
                        utils_logger.log("监测到'点击阅读全文',触发单击事件")
                return True
            elif cur_activity in video_activitys:
                random_play_time = random.randint(25, 90)
                utils_logger.log("等待视频播放完成：" + str(random_play_time))
                time.sleep(random_play_time)  # 等待视频播放
                return True
        elif cur_activity in other_activitys:
            utils_logger.debug("进入非指定详情页面，放弃此次浏览")
            return False
        else:
            utils_logger.log("进入未知页面:" + str(cur_activity))
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
        from handle_callback import HandleCallback

        task.run_task(HandleCallback())
