# coding=utf-8

import os
import sys
import time
import random

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

from helper import utils_image as image_utils, utils_logger
from helper import utils_file as file_utils
from x_aircv.core import Template
from tasks.appium import utils_appium

from tasks.appium.task_appium_base import AbsBasicAppiumTask


class TaskAppiumWeixinExit(AbsBasicAppiumTask):
    """微信退出应用,7点之后重复检测退出微信页面"""

    def __init__(self):
        AbsBasicAppiumTask.__init__(self, "com.tencent.mm", "com.tencent.mm.ui.LauncherUI")

    def is_time_support(self, curent_time=None):
        # 微信任务只支持早上7点之前执行，白天还要使用微信的
        is_run_support = True if curent_time > 700 else False
        utils_logger.log(str(curent_time) + "---> is_run_support(" + str(self.__class__) + "):" + (
            "True" if is_run_support else "False"))
        return is_run_support

    def run_task(self, _handle_callback):
        if AbsBasicAppiumTask.run_task(self, _handle_callback) is False:
            return False
        if self.wait_activity(self.driver, '.plugin.account.ui.LoginPasswordUI') is True:
            utils_logger.log("是登录页面")
            return True
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我'), click_mode="click") is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('设置'), click_mode='click') is not None:
                if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('退出'),
                                          click_mode='click') is not None:
                    if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("退出登录"),
                                              click_mode='click') is not None:
                        # '退出登录'弹框确认
                        if self.query_ele_wrapper(
                                self.get_query_str_within_xpath_only_text('退出', view_type='android.widget.Button'),
                                click_mode='click') is not None:
                            utils_logger.log("点击退出退出账号")
                            time.sleep(10)
                            return False
                        else:
                            self.task_scheduler_failed("退出失败")
                    else:
                        self.task_scheduler_failed("'退出登录'失败")
                else:
                    self.task_scheduler_failed("退出按钮 not found")
            else:
                self.task_scheduler_failed("未检测到'设置'入口")


class TaskAppiumWeixinBase(AbsBasicAppiumTask):
    """进入首页的基类"""

    def __init__(self):
        AbsBasicAppiumTask.__init__(self, "com.tencent.mm", "com.tencent.mm.ui.LauncherUI")

    def is_time_support(self, curent_time=None):
        # 微信任务只支持早上7点之前执行，白天还要使用微信的
        is_run_support = True if curent_time < 700 else False
        utils_logger.log(str(curent_time) + "---> is_run_support(" + str(self.__class__) + "):" + (
            "True" if is_run_support else "False"))
        return is_run_support

    def except_case_in_query_ele(self):
        if AbsBasicAppiumTask.except_case_in_query_ele(self) is True:
            return True
        if self.wait_activity(self.driver, '.plugin.account.ui.LoginPasswordUI', is_ignore_except_case=True,
                              retry_count=1) is True:
            # 微信密码还没有指定
            weixin_pwd = conf_modify.query("", "weixin_password")
            if weixin_pwd is None:
                self.task_scheduler_failed("未指定微信登录密钥")
                return False
            # 自登陆逻辑
            ele_pwd_edt = self.query_ele_wrapper("//android.widget.EditText[@resource-id='com.tencent.mm:id/ji']",
                                                 is_ignore_except_case=True)
            if ele_pwd_edt is not None:
                ele_pwd_edt.send_keys(str(weixin_pwd))
                if self.query_ele_wrapper(
                        self.get_query_str_within_xpath_only_text('登录', view_type='android.widget.Button'),
                        click_mode="click", is_ignore_except_case=True) is not None:
                    utils_logger.log("wait login success")
                    time.sleep(10)  # 等待登录完成
                    return True
                else:
                    self.task_scheduler_failed('找不到登录按钮', is_ignore_except_case=True)
            else:
                self.task_scheduler_failed('在登录界面却找不到密码输入框', is_ignore_except_case=True)
        # # 存储空间清理
        # elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('存储空间不足'),is_ignore_except_case=True,retry_count=0) is not None:
        #     if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('忽略',view_type='android.widget.Button'),is_ignore_except_case=True,click_mode='click') is not None:
        #         return True
        #     else:
        #         self.task_scheduler_failed("无法关闭'清除存储空间'的弹框")
        elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('你的微信帐号于', is_force_match=False),
                                    is_ignore_except_case=True, retry_count=0) is not None:
            # 被踢下线,包含内容"你的微信帐号于10:24在Android设备设备上通过短信登录。如果这不是你的操作，你的短信验证码已经泄漏。请勿转发短信验证码，并排查手机是否被植入木马导致短信被转发。"
            if self.query_ele_wrapper(
                    self.get_query_str_within_xpath_only_text('确定', view_type='android.widget.Button'),
                    click_mode='click', is_ignore_except_case=True, retry_count=0) is not None:
                return True
            else:
                self.task_scheduler_failed("无法关闭被踢下线的弹框")
        return False

    def run_task(self, _handle_callback):
        if AbsBasicAppiumTask.run_task(self, _handle_callback) is False:
            return False
        if self.wait_activity(self.driver, '.ui.LauncherUI') is False:
            self.task_scheduler_failed('why not in main page of weixin')
            return False


class TaskAppiumWeixinJimmieJDJingdonghuiyuan(TaskAppiumWeixinBase):
    '微信-京东会员'

    def run_task(self, _handle_callback):
        if TaskAppiumWeixinBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我'), click_mode="click") is None:
            self.task_scheduler_failed('not found \"我\"')
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('收藏'), click_mode="click") is None:
            self.task_scheduler_failed("\"收藏\"")
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('尊享京东会员新身份', is_force_match=False),
                                  click_mode="click") is None \
                and self.query_only_point_within_text('^尊享京东会员新身份', is_auto_click=True) is None:
            self.task_scheduler_failed('尊享京东会员新身份')
            return False
        if self.query_only_point_within_text('^签$|^签到$', cutted_rect=[0.8, 1, 0.7, 1], is_auto_click=True) is not None:
            if self.query_point_size_within_text('^京豆优惠购$') > 0:
                # 表示进入到签到成功页面
                return True
            else:
                self.task_scheduler_failed('not found 京豆优惠购')
        else:
            self.task_scheduler_failed('未找到右下角-签到按钮')
        return False


class TaskAppiumWeixinJimmieJDCaiYunlianlianfan(TaskAppiumWeixinBase):
    '微信-Jimmie-财运连连翻'

    def run_task(self, _handle_callback):
        if TaskAppiumWeixinBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我'), click_mode="click") is None:
            self.task_scheduler_failed('not found \"我\"')
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('收藏'), click_mode="click") is None:
            self.task_scheduler_failed("\"收藏\"")
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('财运连连翻'), click_mode="click") is None \
                and self.query_only_point_within_text('^财运连连翻$', is_auto_click=True) is None:
            self.task_scheduler_failed('财运连连翻')
            return False
        # TODO：以下仅做测试使用
        if self.query_only_point_within_text('占位符') is not None:
            utils_logger.log("模拟使用占位符")
        else:
            self.task_scheduler_failed('财运连连翻 failed')
        return False


class TaskAppiumWeixinJimmieJDJingdouleyuan(TaskAppiumWeixinBase):
    '微信-Jimmie-京豆乐园'

    def run_task(self, _handle_callback):
        if TaskAppiumWeixinBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我'), click_mode="click") is None:
            self.task_scheduler_failed('not found \"我\"')
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('收藏'), click_mode="click") is None:
            self.task_scheduler_failed("\"收藏\"")
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('这里可以免费领京豆', is_force_match=False),
                                  click_mode="click") is None \
                and self.query_only_point_within_text('^这里可以免费领京豆$', is_auto_click=True) is None:
            self.task_scheduler_failed('这里可以免费领京豆')
            return False
        if self.query_only_point_within_text('^签到领京豆$', is_auto_click=True) is not None:
            utils_logger.log("领取京豆")
            if self.query_point_size_within_text('^知道了$|^京豆稍后会发放到您的账号$') > 0:
                utils_logger.log("签到成功")
                return True
            else:
                self.task_scheduler_failed("解析'我知道了'失败")
                return False
        elif self.query_point_size_within_text(r'^已连续签到\d+天$|^今日邀请\d+位好友完成签到') > 0:
            utils_logger.log("今日已签到")
            return True
        else:
            self.task_scheduler_failed('无法领取京豆')
        return False


class TaskAppiumWeixinJimmieJDPeiyuchang(TaskAppiumWeixinBase):
    '微信-Jimmie-京豆培育舱'

    def run_task(self, _handle_callback):
        if TaskAppiumWeixinBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我'), click_mode="click") is None:
            self.task_scheduler_failed('not found \"我\"')
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('收藏'), click_mode="click") is None:
            self.task_scheduler_failed("\"收藏\"")
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('京豆培育舱'), click_mode="click") is None:
            self.task_scheduler_failed('未找到京豆培育舱')
            return False
        is_view_layout_finished, file_screen_shot = self.wait_view_layout_finish(True)
        if is_view_layout_finished is False:
            utils_logger.log("在指定时限页面还未绘制完成")
            self.task_scheduler_failed('在指定时限页面还未绘制完成')
            return False

        event_position = self.query_only_point_within_text('^(收获京豆|分享加速|培育京豆)$')
        if event_position is None:
            utils_logger.log("未找到指定操作控件")
            self.task_scheduler_failed('未找到指定操作控件')
            return False
        # 构造比对子类
        base_src_img = project_root_path + "/tasks/appium/img/screen_shot_jingdong_jdpyc.png"
        outter_dir = envs.get_out_dir()
        # 收获啦 图标
        img_finish_part = file_utils.generate_suffix_file(raw_file_path=base_src_img, save_to_dir=outter_dir,
                                                          suffix="finish")
        image_path_finish = image_utils.cutted_image_with_scale(base_src_img, img_finish_part, [0.505, 0.7, 0.81, 0.92])
        # 培养中
        # image_path_doing=image_utils.cutted_image_with_scale(scr_path,file_utils.generate_suffix_file(scr_path, suffix="doing"),[0.745,0.93,0.81,0.92])
        # 等待培养
        img_waiting_part = file_utils.generate_suffix_file(raw_file_path=base_src_img, save_to_dir=outter_dir,
                                                           suffix="wating")
        image_path_waiting = image_utils.cutted_image_with_scale(base_src_img, img_waiting_part,
                                                                 [0.265, 0.45, 0.81, 0.92])
        # 分享加速 - 搜索该按钮，用于后面点击收获-以及开始培养
        # image_path_event=image_utils.cutted_image_with_scale(scr_path,file_utils.generate_suffix_file(scr_path, suffix="event"),[0.34,0.63,0.68,0.74])
        # 循环滑动20次，识别待收获的按钮
        for index in range(10):  # 随机滑动十次
            # 截图
            scr_path = utils_appium.get_screen_shots(driver=self.driver, file_directory=self.get_project_output_dir(),
                                                     target_device=self.target_device_name)
            parent_template = Template(scr_path)  # 这里的parenr_template一般使用截图文件
            # 收获京豆
            finish_matchs = Template(image_path_finish).results_within_match_in(parent_template)
            # if finish_matchs is not None:
            #     for match_result_item in finish_matchs:
            #         int_x=int(match_result_item['result'][0])
            #         int_y=int(match_result_item['result'][1])
            #         utils_logger.log("check 按钮范围:",int_x,",",int_y,",600>int_x>0:",(600>int_x>0),",92*1024>100*int_y>1024*81:",(92*1024>100*int_y>1024*81)
            #         is_edge_ok=(600>int_x>0 and 92*1024>100*int_y>1024*81)
            #         if is_edge_ok is False:
            #             utils_logger.log("当前按钮不在范围内，忽略"
            #             continue
            #         utils_logger.log("选中指定item：",match_result_item
            #         if self.safe_tap_in_point(match_result_item['result']) is False:
            #             self.task_scheduler_failed("选中'收获京豆'item失败")
            #             return False
            #         utils_logger.log("收获该item",event_position
            #         if self.safe_tap_in_point(event_position) is False:
            #             self.task_scheduler_failed("收获京豆失败")
            #             return False
            #         utils_logger.log("收获的同时再次点击以开启培养操作,延时操作------------ing..."
            #         time.sleep(2)
            #         if self.safe_tap_in_point(event_position) is False:
            #             self.task_scheduler_failed("再次培育京豆失败")
            #             return False
            #         utils_logger.log("收获的同时再次点击以开启培养操作,延时操作------------end"
            # # 培养京豆
            # waiting_matchs=Template(image_path_waiting).results_within_match_in(parent_template)
            # if waiting_matchs is not None:
            #     for match_result_item in waiting_matchs:
            #         int_x=int(match_result_item['result'][0])
            #         int_y=int(match_result_item['result'][1])
            #         utils_logger.log("check 按钮范围:",int_x,",",int_y,",600>int_x>0:",(600>int_x>0),",92*1024>100*int_y>1024*81:",(92*1024>100*int_y>1024*81)
            #         is_edge_ok=(600>int_x>0 and 92*1024>100*int_y>1024*81)
            #         if is_edge_ok is False:
            #             utils_logger.log("当前按钮不在范围内，认为是有其他元素,触摸以关闭弹窗"
            #             continue
            #         utils_logger.log("选中指定item：",match_result_item
            #         if self.safe_tap_in_point(match_result_item['result']) is False:
            #             self.task_scheduler_failed("无法选中'培育京豆'item")
            #             return False
            #         if self.query_only_point_within_text("^培育京豆$",is_auto_click=True,retry_count=0) is not None:
            #             utils_logger.log("检测到'培育京豆'按钮，需要培育该item",event_position
            # 基于文字'待收获'进行
            shouhuola_point_result = self._query_points_with_text_by_ocr('^收获啦$')
            if shouhuola_point_result is not None:
                for single_point in shouhuola_point_result:
                    if self.safe_tap_in_point(single_point['avaiable_point']) is False:
                        self.task_scheduler_failed("选择'收获啦'失败")
                        continue
                    utils_logger.log("收获该item", event_position)
                    if self.safe_tap_in_point(event_position) is False:
                        self.task_scheduler_failed("收获京豆失败")
                        continue
                    utils_logger.log("收获的同时再次点击以开启培养操作,延时操作------------ing...")
                    time.sleep(2)
                    if self.safe_tap_in_point(event_position) is False:
                        self.task_scheduler_failed("再次培育京豆失败")
                        continue
                    utils_logger.log("收获的同时再次点击以开启培养操作,延时操作------------end")
            # 滑动控件
            if bool(random.getrandbits(1)) is True:
                tab_interval = [0.3, 0.7]
            else:
                tab_interval = [0.7, 0.3]
            self.safe_touch_action(is_down=False, tab_center=0.85, tab_interval=tab_interval, duration=300)
        return True


class TaskAppiumWeixinShenqianxiaozhushou(TaskAppiumWeixinBase):
    '''省钱小助手签到'''

    def run_task(self, _handle_callback):
        if TaskAppiumWeixinBase.run_task(self, _handle_callback) is False:
            return False
        "//android.view.View[@text='']"
        # 需要设置备注为"淘宝省钱小助手"
        if self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text(view_type='android.view.View', text='淘宝省钱小助手',
                                                          is_force_match=False), click_mode='click') is None \
                and self.query_only_point_within_text('^淘宝省钱小助手$', is_auto_click=True) is None:
            self.task_scheduler_failed('not found \"省钱小助手\"')
            return False
        # 搜索输入框
        ele_edit = self.query_ele_wrapper("//android.widget.EditText", rect_scale_check_element_region=[0, 1, 0, 1])
        if ele_edit is None:
            self.task_scheduler_failed('未找到内容数据输入框')
            return False
        else:
            ele_edit.send_keys(u"签到")
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('发送', view_type='android.widget.Button'),
                                  click_mode='click') is not None:
            utils_logger.log("点击发送按钮")
            return True
        else:
            utils_logger.log("找不到发送的按钮")
            self.task_scheduler_failed('找不到发送的按钮')
            return False
        return False
        # if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('发送'),click_mode="click") is not None:
        #     self.task_scheduler_failed('搜索发送按钮')
        # else:
        #     self.task_scheduler_failed('搜索发送按钮失败')
        # return False


class TaskAppiumWeixinZhaohangXinyongkaSign(TaskAppiumWeixinBase):
    '招商信用卡签到领取积分'

    def run_task(self, _handle_callback):
        if TaskAppiumWeixinBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper("//android.view.View[@text='招商银行信用卡']", click_mode="click") is None \
                and self.query_only_point_within_text('^招商银行信用卡$', is_auto_click=True) is None:
            self.task_scheduler_failed('not found \"招商银行信用卡\"')
            return False
        # 截图1
        # screen_shop_first=utils_appium.get_screen_shots(self.driver,self.target_device_name,file_name='zhaohangxinyongka_sign_first.png')
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('领积分', is_force_match=False),
                                  click_mode='click') is None \
                and self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('积分抽奖', is_force_match=False),
                                           click_mode="click") is None:
            self.task_scheduler_failed('not found \"领取任务\"')
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('签到领积分'), click_mode="click") is None \
                and self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('签到领积分', is_force_match=False),
                                           click_mode="click") is None:
            self.task_scheduler_failed('not found \"签到领积分\"')
            return False
        # screen_shop_second=utils_appium.get_screen_shots(self.driver,self.target_device_name,file_name='zhaohangxinyongka_sign_secong.png')
        # 根据图片相似度来取舍
        # return utils.is_img_similary(screen_shop_first,screen_shop_second,90)

        # 等待10秒
        utils_logger.log("TaskAppiumZhaohangXinyongkaSign sleep:", 10)
        time.sleep(10)
        return True


class TaskAppiumWeixinWaziDashangchengBase(TaskAppiumWeixinBase):
    '''
       微信-首页-袜子大商城-领取任务-京东免单/天猫免单
   '''

    def __init__(self, mode):
        TaskAppiumWeixinBase.__init__(self)
        'mode:京东免单 or 天猫免单'
        self.mode = mode

    def notify_task_success(self):
        AbsBasicAppiumTask.notify_task_success(self)
        utils_logger.log("更新上次check时间")
        if self.task_session is not None:
            conf_modify.put(task_tag=self.task_session, key="last_check_task_state_time",
                            value=utils.get_shanghai_time('%Y%m%d%H%M'))

    def run_task(self, _handle_callback):
        if TaskAppiumWeixinBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper("//android.view.View[@text='袜子大商城']", click_mode="click") is None \
                and self.query_only_point_within_text('^袜子大商城$', is_auto_click=True) is None:
            self.task_scheduler_failed('not found \"袜子大商城\"')
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('领取任务'), click_mode="click") is None:
            self.task_scheduler_failed('not found \"领取任务\"')
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(self.mode), click_mode="click") is None:
            self.task_scheduler_failed("not found \"" + self.mode + "\"")
            return False
        if self.query_point_size_within_text('^您在领取冷却中$') > 0:
            utils_logger.log("检测到任务冷却中")
            if self.task_session is not None:
                # TODO：检测到任务冷却中，因此强制把今日所有的该任务都清空(这种方式不够友好)
                conf_modify.put(task_tag=self.task_session, key="today_repeat_count_left", value=0)
            return True
        elif self.query_point_size_within_text('^当前小时任务已抢完$') > 0:
            utils_logger.log('--->检测到当前小时任务已抢光')
            return True
        elif self.query_point_size_within_text('^领取此任务$') > 0:
            self.task_scheduler_failed(message="TaskAppiumWaziDashangchengBase:" + self.mode,
                                       email_title=u'Maybe收到一笔新的袜子商城的任务')
            return True
        else:
            self.task_scheduler_failed('获取新任务失败')
            return False


class TaskAppiumWeixinWaziDashangchengJingDong(TaskAppiumWeixinWaziDashangchengBase):
    def __init__(self):
        TaskAppiumWeixinWaziDashangchengBase.__init__(self, '京东免单')


class TaskAppiumWeixinWaziDashangchengTaobao(TaskAppiumWeixinWaziDashangchengBase):
    def __init__(self):
        TaskAppiumWeixinWaziDashangchengBase.__init__(self, '天猫免单')


class TaskAppiumWeixinJDJRQuanyiCenter(TaskAppiumWeixinBase):
    """
        用于领取使用京东支付后的京豆奖励
        由于京豆有效期为48小时，因此采用每天执行一次
        路径：京东支付-支付-京东支付权益中心
    """

    def except_case_in_query_ele(self):
        if TaskAppiumWeixinBase.except_case_in_query_ele(self) is True:
            return True
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('微信登录'),
                                  is_ignore_except_case=True) is not None \
                and self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('申请获取以下权限:', is_force_match=False),
                                           is_ignore_except_case=True) is not None:
            utils_logger.log("检测到京东授权弹窗信息")
            # 检测到需要京东授权登录窗口校验
            if self.query_ele_wrapper(
                    self.get_query_str_within_xpath_only_text('允许', view_type='android.widget.Button'),
                    click_mode='click', is_ignore_except_case=True) is not None:
                return True
            else:
                self.task_scheduler_failed("无法关闭京东授权弹窗")
        elif self.query_point_size_within_text("^您的微信账号已绑定以上京东账号是否直接登录", is_ignore_except_case=True) is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('登录'), click_mode='click',
                                      is_ignore_except_case=True) is not None:
                return True
            else:
                self.task_scheduler_failed("使用绑定的京东账号登陆失败")
        return False

    def run_task(self, _handle_callback):
        if TaskAppiumWeixinBase.run_task(self, _handle_callback) is False:
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我'), click_mode="click") is None:
            self.task_scheduler_failed('not found \"我\"')
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('收藏'), click_mode="click") is None:
            self.task_scheduler_failed("\"收藏\"")
            return False
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('京东支付权益中心', is_force_match=False),
                                  click_mode='click') is None:
            self.task_scheduler_failed("找不到'京东支付权益中心'")
            return False
        # 解析去赚京豆页面
        for try_index in range(5):
            utils_logger.log("开始检测'立即领取' or '去赚京豆' with index:", try_index)
            if self.query_ele_wrapper(self.get_query_str_by_desc('立即领取'), click_mode="click") is not None \
                    or self.query_only_point_within_text('^立即领取$', is_auto_click=True) is not None:
                if self.query_point_size_within_text('^恭喜你获得京豆$') > 0:
                    return True
                elif self.query_only_point_within_text('^去京东金融APP领取$', is_auto_click=True) is not None:
                    utils_logger.log("打开金融app领取(休眠10s)")
                    if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('即将离开微信，打开其它应用')) is not None:
                        utils_logger.log("通过微信开启另外的应用")
                        if self.query_ele_wrapper(
                                self.get_query_str_within_xpath_only_text('允许', view_type='android.widget.Button'),
                                click_mode='click') is not None:
                            time.sleep(10)
                            continue
                        else:
                            self.task_scheduler_failed("操作'允许'按钮失败")
                            return False
                    else:
                        self.task_scheduler_failed("没检测到'打开其他应用的弹框'")
                        return False
                else:
                    self.task_scheduler_failed('未检测到\"恭喜你获得京豆\"文案')
                    return False
            elif self.query_ele_wrapper(self.get_query_str_by_desc('去赚京豆'), click_mode="click") is not None \
                    or self.query_only_point_within_text('^去赚京豆$', is_auto_click=True) is not None:
                if self.query_ele_wrapper(self.get_query_str_by_desc('暂无京豆返利')) is not None \
                        or self.query_point_size_within_text('^暂无京豆返利$') > 0:
                    return True
                else:
                    self.task_scheduler_failed('why not \"暂无京豆返利\"')
                    return False
            else:
                # 循环无法找到相应元素，发送错误提示并进行下次循环
                self.task_scheduler_failed("循环无法找到相应元素，发送错误提示")
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
