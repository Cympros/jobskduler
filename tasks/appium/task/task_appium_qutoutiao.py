# coding=utf-8
'趣头条'
import os
import sys
import abc
import random
import time
import traceback
import inspect

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

from tasks.appium.task_appium_base import AbsBasicAppiumTask
from tasks.appium import utils_appium
from helper import utils_logger
from handle_callback import HandleCallback


class TaskAppiumQutoutiaoBase(AbsBasicAppiumTask, abc.ABC):
    def __init__(self):
        AbsBasicAppiumTask.__init__(self, "com.jifen.qukan", "com.jifen.qkbase.main.MainActivity",
                                    "com.jifen.qkbase.main.MainActivity")

    def except_case_in_query_ele(self):
        if AbsBasicAppiumTask.except_case_in_query_ele(self) is True:
            return True
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.jifen.qukan:id/nu'), click_mode="click",
                                  is_ignore_except_case=True, retry_count=0) is not None:
            return True
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('开启锁屏阅读'), is_ignore_except_case=True,
                                    retry_count=0) is not None:
            utils_logger.log("检测到开启锁屏的弹框，点击左上角关闭弹框")
            if self.safe_tap_in_point([0, 0]) is False:
                self.task_scheduler_failed('safe_tap_in_point failed')
            else:
                return True
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('以后更新'), click_mode="click",
                                    is_ignore_except_case=True, retry_count=0) is not None:
            utils_logger.log("检测到更新弹框")
            return True
        elif self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text("禁止后不再询问", view_type="android.widget.CheckBox"),
                is_ignore_except_case=True, retry_count=0) is not None:
            # 权限弹框
            if self.query_ele_wrapper(
                    self.get_query_str_within_xpath_only_text("始终允许", view_type="android.widget.Button"),
                    click_mode="click", is_ignore_except_case=True, retry_count=0) is not None:
                return True
        return False


class TaskAppiumQutoutiaoYuedu(TaskAppiumQutoutiaoBase):
    '趣头条浏览文章'

    def except_case_in_query_ele(self):
        if TaskAppiumQutoutiaoBase.except_case_in_query_ele(self) is True:
            return True
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('下载完成后并安装打开', is_force_match=False),
                                  is_ignore_except_case=True, retry_count=0) is not None:
            utils_logger.log("检测到'华为、vivo、oppo等机型，请勿选择“安全安装、官方推荐”选择“继续安装、取消”，否则将无法领取金币'")
            if self.query_ele_wrapper(
                    '//android.widget.FrameLayout//android.widget.FrameLayout//android.widget.FrameLayout//android'
                    '.widget.RelativeLayout//android.widget.RelativeLayout//android.view.View',
                    click_mode='click', is_ignore_except_case=True) is not None:
                return True
            else:
                self.task_scheduler_failed("检测到'华为、vivo、oppo等机型，请勿选择“安全安装、官方推荐”选择“继续安装、取消”，否则将无法领取金币',但是无法关闭")
        return False

    def run_task(self, handle_callback):
        if TaskAppiumQutoutiaoBase.run_task(self, handle_callback) is False:
            return False
        # 最多浏览15次，因为一次大约需要1分钟左右时间
        for_each_size = int(random.randint(5, 15))
        for index in range(for_each_size):
            # 观测是否直接抛异常导致回到桌面
            if utils_appium.get_cur_act(self.driver) == '.Launcher':
                utils_logger.log("运行过程中，软件回到了桌面程序，退出浏览任务")
                return False
            utils_logger.log("开启第(" + str(index) + "/" + str(for_each_size) + ")次浏览")
            # 循环回到首页
            def_main_activity = 'com.jifen.qkbase.main.MainActivity'
            if utils_appium.back_to_target_activity(self.driver, def_main_activity) is True:
                try:
                    self.browser_news(def_main_activity)
                except Exception as e:
                    utils_logger.log("browser_news caught exception:", traceback.format_exc())
            else:
                utils_logger.log("无法回退至首页，没办法执行新闻浏览任务")
                break
        return True

    def browser_news(self, main_activity):
        # 需要进入app手动设置关心的栏目：最多支持7个
        module_text = random.choice([u'关注', u'推荐', u'上海', u'娱乐', u'旅行', u'历史', u'汽车', u'军事', u'情感', u'游戏', u'军事'])
        utils_logger.log('--->module_text:', module_text)
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(module_text), click_mode="click",
                                  retry_count=0) is None:
            utils_logger.log('找不到\"' + module_text + '\"板块,不过继续在当前栏目浏览')
        is_view_inflated, scr_shots = self.wait_view_layout_finish(True)
        if is_view_inflated is False:
            self.task_scheduler_failed('页面还未绘制完成，please check')
            return False
        # 搜索应该阅读的文章
        scroll_size = int(random.randint(0, 20))
        utils_logger.debug("页面滚动次数：", scroll_size)
        for index in range(scroll_size):
            # 滑动以选择文章开启阅读任务
            self.safe_scroll_by(tab_interval=[float(random.uniform(0.6, 0.8)), 0.2])
        news_activitys = ['.content.view.activity.NewsDetailActivity', '.content.newsdetail.news.NewsDetailActivity',
                          '.content.newsdetail.news.NewsDetailNewActivity']
        video_activitys = ['.content.view.activity.VideoNewsDetailActivity',
                           '.content.newsdetail.video.VideoNewsDetailActivity',
                           '.content.newsdetail.video.VideoNewsDetailNewActivity',
                           '.content.shortvideo.ShortVideoDetailsActivity',
                           '.content.videodetail.VideoDetailsActivity']
        image_activitys = ['.imagenews.ImageNewsDetailActivity', '.content.imagenews.ImageNewsDetailActivity',
                           '.content.imagenews.ImageNewsDetailNewActivity']
        other_activitys = ['.content.view.activity.ImagePagersActivity', '.content.imagenews.ImagePagersActivity',
                           'com.iclicash.advlib.ui.front.ADBrowser',
                           '.PackageInstallerActivity', 'com.jifen.qkbase.view.activity.WebActivity', '.WebActivity',
                           'com.jd.lib.productdetail.ProductDetailActivity',
                           '.PackageInstallerActivity', '.open.InterfaceActivity', '.QuKanActivity',
                           'com.jifen.qkbase.web.WebActivity', '.Launcher',
                           '.lightbrowser.LightBrowserActivity', '.schemedispatch.BdBoxSchemeDispatchActivity']
        # 随便点击，选择指定文章开始读取
        for tab_index in range(10):
            if utils_appium.get_cur_act(self.driver) != main_activity:
                utils_logger.log("尝试进入文章时发现不在新闻列表页,直接退出")
                return False
            self.safe_tap_in_point([random.randint(100, 400), random.randint(200, 800)])
            if self.wait_activity(driver=self.driver, target=news_activitys + video_activitys) is True:
                utils_logger.debug("成功进入某个详情页面")
                break
            else:
                # 进入详情页失败,则先回退至首页
                if utils_appium.back_to_target_activity(self.driver, main_activity) is False:
                    utils_logger.log("等待进入详情页失败,且无法回退至首页,则直接退出浏览")
                    return False
                self.safe_scroll_by(tab_interval=[float(random.uniform(0.65, 0.35)), 0.35])
        # 判断是否在详情页面
        cur_activity = utils_appium.get_cur_act(self.driver)
        if cur_activity == main_activity:
            self.task_scheduler_failed('why 还在首页?')
            return False
        # 根据页面调用指定阅读策略
        utils_logger.debug("cur_activity:", cur_activity)
        if cur_activity in news_activitys + video_activitys:
            # 判断是否有有效的进度条
            if self.query_ele_wrapper(
                    '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout'
                    '/android.widget.FrameLayout/android.widget.ImageView[3]',
                    is_ignore_except_case=True) is None:
                if self.query_ele_wrapper(
                        '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout'
                        '/android.widget.ImageView',
                        is_ignore_except_case=True, click_mode='click') is not None:
                    # 说明需要敲金蛋
                    utils_logger.log("敲击金蛋领取奖励")
                    return True
                else:
                    utils_logger.log("详情页无阅读积分进度框,是无效阅读")
                    return False

            if cur_activity in news_activitys:
                # 开始模拟阅读
                time_to_foreach = random.randint(10, 30)  # 5~10s，因为每30秒就可以获得10积分的奖励
                period = 0.2  # 每次浏览间隔，单位：秒
                for index in range(int(float(time_to_foreach) / period)):
                    if utils_common.random_boolean_true(0.65) is True:
                        tab_interval = [0.65, 0.35]
                    else:
                        tab_interval = [0.25, 0.75]
                    utils_logger.debug(
                        "[" + str(time_to_foreach) + "] for tab_interval[" + str(tab_interval) + "] with index:" + str(
                            index))
                    if self.safe_scroll_by(tab_interval=tab_interval, duration=int(float(period * 1000))) is False:
                        utils_logger.log("----> safe_scroll_by caught exception")
                        break
                    # 每滑动一次,均判断是否还在详情页
                    scroll_activity = utils_appium.get_cur_act(self.driver)
                    if scroll_activity not in news_activitys:
                        utils_logger.log("浏览过程中退出新闻页: ", scroll_activity)
                        break
                return True
            elif cur_activity in video_activitys:
                video_play_time = random.randint(15, 30)
                utils_logger.log("等待视频播放完成：" + str(video_play_time))
                time.sleep(video_play_time)  # 休眠45秒
                return True
        elif cur_activity in image_activitys + other_activitys:
            utils_logger.log("进入非指定详情页面，放弃此次浏览")
            return False
        else:
            self.task_scheduler_failed(message='未知页面:' + cur_activity, email_title="UnknownPage")
            return False


class TaskAppiumQutoutiaoCoreShiduanJiangli(TaskAppiumQutoutiaoBase):
    """首页-右上角-时段奖励"""

    def except_case_in_query_ele(self):
        if TaskAppiumQutoutiaoBase.except_case_in_query_ele(self) is True:
            return True
        # 解决意外进入"我的等级"页面
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("我的等级"),
                                  is_ignore_except_case=True) is not None:
            # 点击返回，返回上一层
            if self.query_ele_wrapper(
                    "//android.widget.LinearLayout//android.widget.FrameLayout//android.widget.RelativeLayout"
                    "//android.widget.RelativeLayout//android.widget.RelativeLayout//android.widget.ImageView",
                    click_mode='click', is_ignore_except_case=True) is not None:
                return True
            else:
                self.task_scheduler_failed("检测到'我的等级页面',但未推出")
                return False
        return False

    def run_task(self, _handle_callback):
        if TaskAppiumQutoutiaoBase.run_task(self, _handle_callback) is False:
            return False
        # 注释:可能第一次点击会是成功签到，但是此时中间弹框会快速消失，因此再启用第二次尝试点击以检测弹框
        btn_ele_xpath = '//android.widget.FrameLayout//android.widget.LinearLayout//android.widget.FrameLayout' \
                        '//android.widget.LinearLayout//android.widget.FrameLayout//android.widget.RelativeLayout' \
                        '//android.widget.FrameLayout//android.widget.LinearLayout//android.widget.RelativeLayout' \
                        '//android.widget.RelativeLayout//android.widget.RelativeLayout//android.widget.FrameLayout' \
                        '//android.widget.TextView '
        # 第一次点击小时签到
        if self.query_ele_wrapper(btn_ele_xpath, click_mode="click", time_wait_page_completely_resumed=5,
                                  retry_count=0) is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('时段奖励'), retry_count=0) is not None:
                utils_logger.log("成功弹出时段奖励弹框")
                return True
            else:
                # 若第一次是成功签到，发起第二次查询是否已成功签到的检测
                if self.query_ele_wrapper(btn_ele_xpath, click_mode="click", retry_count=0) is not None:
                    if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('时段奖励'),
                                              retry_count=0) is not None:
                        utils_logger.log("成功弹出时段奖励弹框")
                        return True
                else:
                    self.task_scheduler_failed('第二次未搜索到右上角按钮')
                    return False
        else:
            self.task_scheduler_failed('第一次未搜索到右上角按钮')
            return False
        return False


class TaskAppiumQutoutiaoTaskCenter(TaskAppiumQutoutiaoBase):
    def run_task(self, _handle_callback):
        if TaskAppiumQutoutiaoBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('任务', view_type='android.widget.Button'),
                                  click_mode="click", time_wait_page_completely_resumed=5) is None:
            utils_logger.log('找不到\"任务\"按钮')
            return False
        # # 每次进入'我的'页面，都会下拉刷新一次，因此point位置会变更，故而加上个time_wait_page_completely_resumed
        # if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('任务中心'),click_mode="click",time_wait_page_completely_resumed=5) is None:
        #     self.task_scheduler_failed('没找到任务中心')
        #     return False
        return True


class TaskAppiumQutoutiaoSign(TaskAppiumQutoutiaoTaskCenter):
    """任务中心-签到：进入这个页面即表示领取成功"""

    def run_task(self, _handle_callback):
        if TaskAppiumQutoutiaoTaskCenter.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text(text='明天签到可领', view_type='android.view.View')) is not None \
                or self.query_ele_wrapper(
            self.get_query_str_within_xpath_only_text(text='明天签到可领', view_type='android.view.View',
                                                      attribute='content-desc')) is not None \
                or self.query_ele_wrapper(
            self.get_query_str_within_xpath_only_text(text='已签', view_type='android.view.View')) is not None \
                or self.query_ele_wrapper(
            self.get_query_str_within_xpath_only_text(text='已签', view_type='android.view.View',
                                                      attribute='content-desc')) is not None:
            utils_logger.log("今日已签到")
            return True
        else:
            self.task_scheduler_failed('为何发现今日未签到')
            return False


class TaskAppiumQutoutiaoOpenBaoxiang(TaskAppiumQutoutiaoTaskCenter):
    '任务中心-开宝箱分享-开宝箱'
    '签到'

    def run_task(self, _handle_callback):
        if TaskAppiumQutoutiaoTaskCenter.run_task(self, _handle_callback) is False:
            return False
        # 循环滚动直至搜索到元素
        upload_files = []
        for i in range(10):
            if self.query_ele_wrapper("//android.view.View[@content-desc='开宝箱分享']") is not None:
                utils_logger.log("检测到\"开启宝箱成功\"")
                break

            utils_logger.log('未找到开宝箱的按钮')
            utils_logger.log("TaskAppiumQtoutiaoOpenBaoxiang swipe of index：", i)
            self.safe_scroll_by(tab_center=0.4, is_down=True, tab_interval=[0.65, 0.35])
            continue
        # 检测到
        if self.query_ele_wrapper("//android.view.View[@content-desc='开启宝箱']", click_mode="click") is not None:
            utils_logger.log("检测到\"开启宝箱成功\"")
        else:
            utils_logger.log("\"开启宝箱\"正在倒计时")
            return True

        # 判断是否进入'邀请好友' - 即开宝箱页面
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('邀请好友')) is None:
            self.task_scheduler_failed('未进入\"邀请好友\"界面', upload_files=upload_files)
            return False
        # 拆宝箱页面
        if self.query_ele_wrapper("//android.view.View[@content-desc='开宝箱']", click_mode="click") is not None:
            utils_logger.log("TODO:开启宝箱后的反应")
            # TODO:弹框中包含'恭喜获得宝箱奖励',但无法使用appium方式检测，需要使用query_point(暂时放弃，次数善用)
            # if self.query_ele_wrapper(self)
            # self.task_scheduler_failed('TODO:开启宝箱后的反应')
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('明天再来')) is not None:
            utils_logger.log("今日已没有机会")
            return True
        else:
            self.task_scheduler_failed('解析异常')
            return False
        return False


class TaskAppiumQutoutiaoGrandTotalJiangli(TaskAppiumQutoutiaoTaskCenter):
    '''
        任务中心-累计阅读时长达到60分钟
        由于该任务需要新闻浏览任务执行足够多次，所以让该任务稍微晚点指定
    '''

    def is_time_support(self, curent_time=None):
        is_run_support = True if 1600 < curent_time else False
        utils_logger.log(str(curent_time) + "---> is_run_support(" + str(self.__class__) + "):" + (
            "True" if is_run_support else "False"))
        return is_run_support

    def run_task(self, _handle_callback):
        if TaskAppiumQutoutiaoTaskCenter.run_task(self, _handle_callback) is False:
            return False
        for index in range(10):
            utils_logger.log("TaskAppiumQtoutiaoGrandTotalJiangli for-each:", index)
            if self.query_ele_wrapper("//android.view.View[@content-desc='累计阅读时长达到60分钟']", click_mode="click",
                                      rect_scale_check_element_region=[0, 1, 0, 1]) is not None:
                utils_logger.log("检测到\"累计阅读时长达到60分钟\"")
                break
            self.safe_scroll_by(tab_center=0.4, is_down=True, tab_interval=[0.65, 0.35])
        if self.query_ele_wrapper("//android.view.View[@content-desc='累计阅读时长达到60分钟']") is not None:
            if self.query_ele_wrapper("//android.view.View[@content-desc='立即阅读']") is not None:
                utils_logger.log("阅读时间未达到60分钟")
                return False
            else:
                utils_logger.log("已阅读满60分钟")
                return True
        else:
            self.task_scheduler_failed('未检测到\"累计阅读时长达到60分钟\"')
            return False
        return False


if __name__ == '__main__':
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

        task.run_task(HandleCallback())
