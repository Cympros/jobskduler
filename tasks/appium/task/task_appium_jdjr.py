# coding=utf-8
import time
import os
import sys

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.append(project_root_path)

from tasks.appium.task_appium_base import AppiumBaseTask
# from helper import utils_logger


class TaskAppiumJDJRSignBase(AppiumBaseTask):
    '''
        用于进入京东金融的首页
    "'''

    def __init__(self):
        AppiumBaseTask.__init__(self, "com.jd.jrapp", "com.jd.jrapp.WelcomeActivity")

    def __deal_within_login(self):
        '处理在登录界面的情况'
        # 切换成京东账号一键登录
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('京东APP一键登录'), click_mode="click",
                                  is_ignore_except_case=True) is not None:
            utils_logger.log("检测到'京东APP一键登录'")
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('京东一键登录'), click_mode="click",
                                    is_ignore_except_case=True) is not None:
            utils_logger.log("检测到'京东一键登录'")
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('更多'), click_mode="click",
                                    is_ignore_except_case=True) is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('京东一键登录'), click_mode="click",
                                      is_ignore_except_case=True) is None:
                self.task_scheduler_failed("有'更多',但无'京东一键登录'")
                return False
        else:
            self.task_scheduler_failed("无更多入口")
            return False
        # 以下是跳转到京东app应用后的展示页面对应的逻辑判断
        if self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('使用京东账号授权并登录', view_type="android.view.View"),
                is_ignore_except_case=True) is not None \
                or self.query_point_size_within_text('^使用京东账号授权并登录$') > 0:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('确认登录', view_type="android.view.View"),
                                      click_mode="click", is_ignore_except_case=True) is not None \
                    or self.query_only_point_within_text(search_text='^确认登录$', is_auto_click=True) is not None:
                return True
            else:
                self.task_scheduler_failed("无'确认登录'")
                return False
        else:
            self.task_scheduler_failed("无'京东账号授权页面")
            return False
        return False

    def except_case_in_query_ele(self):
        if AppiumBaseTask.except_case_in_query_ele(self) is True:
            return True
        if self.wait_activity(self.driver, ['.ver2.account.security.GestureLockActivity',
                                            '.bm.zhyy.account.security.GestureLockActivity'],
                              is_ignore_except_case=True) is True:
            # 手势界面:不予处理，邮件通知需要让用户将手势开关关闭
            self.task_scheduler_failed("请务必关闭手势，提高软件运行效率")
            return False
        elif self.wait_activity(self.driver,
                                ['.ver2.account.login.ui.LoginActivity', '.bm.zhyy.login.ui.LoginActivity'],
                                is_ignore_except_case=True) is True \
                and self.__deal_within_login() is True:
            utils_logger.log("---> 检测到需要登录界面")
            return True
        elif self.query_ele_wrapper(self.get_query_str_by_viewid('com.jd.jrapp:id/ibtn_zc_product_notice_board_close'),
                                    is_ignore_except_case=True, click_mode="click", retry_count=0) is not None:
            utils_logger.log("search element with close")  # 搜索到桌面弹框，底部有关闭按钮部分
            return True
        # 检测到软件升级
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('软件升级'), is_ignore_except_case=True,
                                    retry_count=0) is not None:
            if self.query_ele_wrapper(self.get_query_str_by_viewid('com.jd.jrapp:id/cancel'), retry_count=0,
                                      is_ignore_except_case=True, click_mode="click") is None:
                self.task_scheduler_failed("检索到软件升级，但是没有检测到关闭按钮")
                return False
            return True
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('如果非本人操作，登录密码可能已泄露，本设备将会被强制退出登录'),
                                    retry_count=0, is_ignore_except_case=True) is not None:
            if self.query_ele_wrapper(self.get_query_str_by_viewid('com.jd.jrapp:id/btn_ok'), retry_count=0,
                                      click_mode="click", is_ignore_except_case=True) is None:
                self.task_scheduler_failed('关闭单点登录风险提示框失败')
                return False
            return True
        return False

    def run_task(self):
        if AppiumBaseTask.run_task(self) is False:
            return False
        search_fliter = ['.ver2.main.MainActivity', '.ver2.account.security.GestureLockActivity',
                         '.bm.zhyy.account.security.GestureLockActivity']
        if not self.wait_activity(self.driver, search_fliter, retry_count=20):
            self.task_scheduler_failed("not in target activity")
            return False


class TaskAppiumJDJRQuanyiCenter(TaskAppiumJDJRSignBase):
    """
        desc:废弃，使用'微信-收藏'的方案进入
        用于领取使用京东支付后的京豆奖励
        由于京豆有效期为48小时，因此采用每天执行一次
        路径：京东支付-支付-京东支付权益中心
    """

    def run_task(self):
        if TaskAppiumJDJRSignBase.run_task(self) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.jd.jrapp:id/secondLayout'),
                                  click_mode="click") is None \
                and self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('支付'), click_mode="click") is None:
            self.task_scheduler_failed('找不到\"首页-支付\"按钮')
            return False
        # 滚动页面直至找到元素
        search_result = False
        for scroll_index in range(10):
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('京豆单单返'), click_mode='click',
                                      is_ignore_except_case=True) is not None \
                    or self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('权益中心', is_force_match=False),
                                              click_mode="click", is_ignore_except_case=True) is not None:
                search_result = True
                break
            utils_logger.log("--->开始滚动第", scroll_index, "次")
            if self.safe_touch_action(tab_interval=[0.6, 0.4]) is True:
                time.sleep(3)  # 这个时候滚动完了，可能页面还没有静止，因此延时等待下
        if search_result is False:
            self.task_scheduler_failed("not found '权益中心'按钮")
            return False
        # 解析去赚京豆页面
        if self.query_ele_wrapper(self.get_query_str_by_desc('去赚京豆'), click_mode="click") is not None \
                or self.query_only_point_within_text('^去赚京豆$', is_auto_click=True) is not None:
            if self.query_ele_wrapper(self.get_query_str_by_desc('暂无京豆返利')) is not None \
                    or self.query_point_size_within_text('^暂无京豆返利$') > 0:
                return True
            else:
                self.task_scheduler_failed('why not \"暂无京豆返利\"')
                return False
        elif self.query_ele_wrapper(self.get_query_str_by_desc('立即领取'), click_mode="click",
                                    time_wait_page_completely_resumed=15) is not None \
                or self.query_only_point_within_text('^立即领取$', is_auto_click=True) is not None:
            if self.query_point_size_within_text('^恭喜你获得京豆$') > 0:
                return True
            else:
                self.task_scheduler_failed('未检测到\"恭喜你获得京豆\"文案')
                return False
        else:
            self.task_scheduler_failed('not found \"去赚京豆\"')
            return False


class TaskAppiumJDJRSign(TaskAppiumJDJRSignBase):
    '''
        task:京东金融签到:首页-我-签到
        路径：首页-我-早起打卡
    '''

    def run_task(self):
        if TaskAppiumJDJRSignBase.run_task(self) is False:
            return False
        # 有可能此时还未登录，因此需要手动触发整个页面进入'登录'模块：'Hi，我们为你准备了新手礼'部分作为入口
        if self.query_ele_wrapper("//android.widget.TextView[@text='登录' and @resource-id='com.jd.jrapp:id/tv_btn']",
                                  click_mode='click', retry_count=0, time_wait_page_completely_resumed=10) is not None:
            # 这里触发进入登录模块，后续的方法负责接力登录模块的处理
            utils_logger.log("--->说明此时还没有登录，因此由上面的query方法触发进入登录模块")
        if self.query_ele_wrapper(self.get_query_str_by_viewid("com.jd.jrapp:id/home_title_portrait"),
                                  click_mode='click') is None:
            self.task_scheduler_failed("未找到左上角用户头像")
            return False
        # 个人中心-早起打卡的前一个tab
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('签到'), click_mode="click") is not None \
                or self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("已签", is_force_match=False),
                                          click_mode="click") is not None \
                or self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("连签", is_force_match=False),
                                          click_mode="click") is not None:
            # 检测是否在登录界面,通过检测标题
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("签到")) is None:
                self.task_scheduler_failed("未进入含'签到'标题字眼的界面")
                return False

        # 支持单个中文字符匹配
        if self.query_only_point_within_text("^签到领钢*", is_auto_click=True) is not None \
                or self.query_only_point_within_text(r'^再签.天有(惊喜|礼)$', is_auto_click=True) is not None:
            # 废弃：or self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('签到成功，并获得连续礼包')) is not None \
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('今天已签到，明天再来吧~')) is not None \
                    or self.query_ele_wrapper("//android.view.View[@content-desc='签到成功，并获得连续礼包']") is not None \
                    or self.query_only_point_within_text('^签到成功$|^签到成功,并获得连续礼包$|^今天已签到,明天再来吧($|~$)') is not None:
                return True
            else:
                self.task_scheduler_failed(message="搜索成功字眼失败")
                return False

        else:
            self.task_scheduler_failed("未找到可触发'签到的按钮'")
            return False


class TaskAppiumJDJRDailyClockOn(TaskAppiumJDJRSignBase):
    '''
        task:京东金融-每日打卡 --> 路径：首页-我-早起打卡
        - 需要开通免密支付
    '''

    def task_scheduler_failed(self, message, email_title=u'Error', is_page_source=True, is_scr_shot=True,
                             upload_files=[]):
        TaskAppiumJDJRSignBase.task_scheduler_failed(self, message=message, email_title=email_title,
                                                   is_page_source=is_page_source, is_scr_shot=is_scr_shot,
                                                   upload_files=upload_files)

    def run_task(self):
        if TaskAppiumJDJRSignBase.run_task(self) is False:
            return False
        # 这里避免多层次class精准定位：响应慢
        if self.query_ele_wrapper(self.get_query_str_by_viewid('com.jd.jrapp:id/home_title_portrait'),
                                  click_mode='click') is None:
            self.task_scheduler_failed("not found '个人中心'入口按钮")
            return False
        # if self.query_ele_wrapper(query_str="//android.view.ViewGroup[@resource-id='com.jd.jrapp:id/fourthLayout']",click_mode="click") is None \
        #         and self.query_ele_wrapper(query_str="//android.widget.RelativeLayout[@resource-id='com.jd.jrapp:id/fourthLayout'",click_mode="click") is None \
        #         and self.query_ele_wrapper(query_str='//android.widget.TextView[@text="我"]',click_mode="click") is None:
        #     self.task_scheduler_failed("not found '我'的按钮")
        #     return False
        # 延迟：因为首页里面的几个tab特别喜欢延迟加载
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('早起打卡'), click_mode="click",
                                  time_wait_page_completely_resumed=5) is not None:
            if self.query_ele_wrapper("//android.view.View[@content-desc='打卡']", click_mode="click") is not None \
                    or self.query_only_point_within_text('^打卡$', is_auto_click=True) is not None:
                if self.query_only_point_within_text('^继续坚持一天$', is_auto_click=True) is not None:
                    time.sleep(15)  # 等待页面加载完成，这里碰到中心循环进度条的问题
                    # 注：继续坚持一天 --> 底部弹出立即支付的按钮
                    # self.task_scheduler_failed('TODO:解析\"继续坚持一天\"之后的逻辑')
                    if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('立即支付'),
                                              click_mode="click") is not None:
                        if self.query_ele_wrapper("//android.view.View[@content-desc='支付成功 记得明早打卡哦']") is not None \
                                or self.query_only_point_within_text('^支付成功记得明早打卡哦$') is not None:
                            return True
                        else:
                            self.task_scheduler_failed("没检测到'支付成功'标识")
                            return False
                    else:
                        self.task_scheduler_failed("没找到'立即支付'按钮")
                        return False
                else:
                    self.task_scheduler_failed('why not check 继续坚持一天')
                    return False
            elif self.query_ele_wrapper("//android.view.View[contains(@content-desc,'打卡倒计时')]") is not None \
                    or self.query_point_size_within_text('^打卡倒计时*') > 0:
                utils_logger.log("检测打\"打卡倒计时\"")
                return True
            elif self.query_ele_wrapper("//android.view.View[@content-desc='支付 1 元参与挑战']",
                                        click_mode="click") is not None \
                    or self.query_only_point_within_text('^支付1元参与挑战$', is_auto_click=True) is not None:
                if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('立即支付'),
                                          click_mode="click") is not None:
                    utils_logger.log("---> wait for 支付完成")
                    time.sleep(8)  # 等待支付完成
                    # 若开通免密支付，则会直接直接支付成功
                    if self.query_ele_wrapper("//android.view.View[@content-desc='支付成功 记得明早打卡哦']") is not None:
                        return True
                    else:
                        self.task_scheduler_failed("why not 解析到'支付成功'标识")
                        return False
                else:
                    self.task_scheduler_failed("why 底部没有出现立即支付的按钮")
                    return False
            else:
                self.task_scheduler_failed('进入早起打卡页面后解析元素失败')
                return False
        else:
            self.task_scheduler_failed('为什么找不到首页-早起打卡')
            return False
        return False

    def is_time_support(self, curent_time=None):
        # 打卡时间：5:00 - 8:00
        is_run_support = True if 500 < curent_time < 800 else False
        utils_logger.log(str(curent_time) + "---> is_run_support(" + str(self.__class__) + "):" + (
            "True" if is_run_support else "False"))
        return is_run_support


if __name__ == '__main__':
    tasks = ['TaskAppiumJDJRDailyClockOn', 'TaskAppiumJDJRQuanyiCenter', 'TaskAppiumJDJRSign']
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
