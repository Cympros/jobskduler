# coding=utf-8

# 定义appium初始化环境

import os
import sys

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../')
sys.path.insert(0, project_root_path)

try:
    import appium
except:
    # https://github.com/appium/python-client#getting-the-appium-python-client
    os.system('pip install Appium-Python-Client')
    import appium
import time
import traceback
from helper import envs
from helper import utils_common
from helper import utils_logger
# from helper import utils_image as image_utils
# from helper import utils_file as file_utils
from helper import utils_android
from tasks.task_base import BaseTask
from tasks.appium import utils_appium
from x_ocr import core as ocr_utils
from x_aircv.core import Template

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class BasicAppiumTask(BaseTask):
    def __init__(self, target_application_id=None, launch_activity=None):
        BaseTask.__init__(self)
        self.driver = None
        self.target_device_name = None
        self.appium_port = 4723
        self.appium_port_bp = None

        self.target_application_id = target_application_id
        self.launch_activity = launch_activity
        self.upload_files = []  # 待上传至远端的文件列表

    def wait_activity(self, driver, target, check_period=1, retry_count=10,
                      is_ignore_except_case=False):
        """activity等待时添加弹框过滤函数
        :param driver: 
        :param target: 
        :param check_period: 
        :param retry_count: 
        :param is_ignore_except_case: 
        :return: boolean
        """
        utils_logger.log("BasicAppiumTask wait_activity")
        # query_activity_status: true or false
        # 第一次搜索时retry_count设置为1次(即一秒)，以避免wait_activity_with_status的重试时间内权限弹框被系统倒计时逻辑关闭
        if utils_appium.wait_activity_with_status(driver=driver, target=target,
                                                  check_period=check_period,
                                                  retry_count=1) is True:
            return True
        for index in range(20):
            if is_ignore_except_case is False and self.except_case_in_query_ele() is True:
                utils_logger.log(
                    "---> except_case_in_query_ele not False,表示except_case_in_query_ele需要重复执行：",
                    index)
            else:
                break
        query_activity_status = utils_appium.wait_activity_with_status(driver=driver, target=target,
                                                                       check_period=check_period,
                                                                       retry_count=retry_count)
        return query_activity_status

    def write_page_resource_into_file(self, suffix="normal"):
        """将pageresource写入文件"""
        if self.driver is None:
            return
        pgres = utils_appium.get_pg_source(self.driver)
        if pgres is not None:
            utils_logger.log(">> page_resource write to file ")
            file_page_resource = envs.get_out_dir() + "page_resource_" + suffix + ".txt"
            # 删除历史文件
            if os.path.exists(file_page_resource) is True:
                os.remove(file_page_resource)
            # 写入当前资源
            with open(file_page_resource, 'w') as f:
                f.write(pgres)
            self.upload_files.append(file_page_resource)

    def write_screen_shot_into_file(self, suffix="normal"):
        """将截图文件写入待上传列表"""
        if self.driver is None:
            return
        scr_file_path = os.path.abspath(envs.get_out_dir() + "/screen_shot_" + suffix + ".png")
        scr_path = utils_appium.get_screen_shots(driver=self.driver,
                                                 target_device=self.target_device_name,
                                                 file_path=scr_file_path)
        if scr_path is not None:
            utils_logger.log("screen shot write to file ")
            self.upload_files.append(scr_path)

    def task_scheduler_failed(self, message, email_title=u'异常信息', is_page_source=True,
                              is_scr_shot=True, upload_files=[],
                              exception_info=None):
        'upload_files：可以允许自定义添加待上传的文件'
        self.upload_files.extend(upload_files)
        if message is not None:
            utils_logger.log("message:", message)
        if self.upload_files is not None and len(self.upload_files) > 0:
            utils_logger.log("task_scheduler_failed in BasicAppiumTask with upload_files:",
                             list(set(self.upload_files)))
        msgs = {'device_name': self.target_device_name,
                'device_version': utils_android.get_deivce_android_version(
                    device=self.target_device_name),
                'device_brand': utils_android.get_brand_by_device(self.target_device_name),
                'device_model': utils_android.get_model_by_device(self.target_device_name),
                'device_resolution': utils_android.get_resolution_by_device(
                    self.target_device_name),
                'app_version': utils_android.get_app_version_by_applicaionid(
                    self.target_device_name,
                    self.target_application_id),
                'raw_message': message,
                }
        if self.driver is not None:
            msgs['current_activity'] = utils_appium.get_cur_act(self.driver)
        # 截取日志并上传
        default_log_file_path = utils_logger.get_log_file()
        self.upload_files.append(default_log_file_path)
        self.upload_files.append(default_log_file_path + ".1")

        if is_page_source is True:
            self.write_page_resource_into_file()
        if is_scr_shot is True:
            self.write_screen_shot_into_file()
        # 必须把self作为第一个参数传进去
        BaseTask.task_scheduler_failed(self, message=msgs, email_title=email_title,
                                       upload_files=list(set(self.upload_files)),
                                       exception_info=exception_info)

    def register_config(self, xargs_dict=None):
        BaseTask.register_config(self, xargs_dict)
        self.target_device_name = xargs_dict.get('device_name')
        self.appium_port = xargs_dict.get('appium_port')
        self.appium_port_bp = xargs_dict.get('appium_port_bp')

    def whether_support_device_type(self, device_type):
        if BaseTask.whether_support_device_type(self, device_type) is False:
            return False
        if device_type != "android":
            return False
        return True

    def is_need_setting_input_manager(self):
        return False

    def run_task(self):
        if BaseTask.run_task(self) is False:
            return False
        if self.target_device_name is not None:  # 未指定设备，则采用默认设备，那么appium端口也无须校验
            # 分配appium服务端口
            if self.appium_port is None or self.appium_port_bp is None:
                self.task_scheduler_failed("未指定appium服务端口")
                return False
        # 检查设备在线状态
        if self.target_device_name is not None:
            device_status = utils_android.get_device_statue(self.target_device_name)
            if device_status != "device":
                # 尝试重连
                if self.target_device_name.endswith(":5555") is True:
                    utils_common.exec_shell_cmd("adb -s " + self.target_device_name + " disconnect")
                    utils_common.exec_shell_cmd("adb connect " + self.target_device_name)
                utils_logger.log("[" + self.target_device_name + "]设备不在线", device_status)
                return False
        else:
            connected_devcies = utils_android.get_connected_devcies()
            if connected_devcies is not None and len(connected_devcies) > 0:
                self.target_device_name = connected_devcies[0]
        # 检查是否设备已连接
        if self.target_device_name is None:
            self.task_scheduler_failed("未连接设备")
            return False
        # 检查应用是否安装
        check_installed_response, response_errror = utils_android.is_app_installed(
            self.target_device_name,
            self.target_application_id)
        if response_errror is None and check_installed_response is None:
            utils_logger.log("当前应用未安装", "device_name:<" + str(self.target_device_name) + ">",
                             "包名<" + str(self.target_application_id) + ">",
                             "ResumedAct<" + utils_android.get_top_focuse_activity(
                                 self.target_device_name) + ">")
            return False

        # 实例化该应用对应的driver对象
        try:
            self.driver = utils_appium.get_driver_by_launch_app(self.target_application_id,
                                                                self.launch_activity,
                                                                self.target_device_name,
                                                                self.is_need_setting_input_manager(),
                                                                self.appium_port,
                                                                self.appium_port_bp)
        except Exception as exception:
            traceback.print_exc()
            except_name = exception.__class__.__name__
            if except_name == "MaxRetryError":
                utils_common.exec_shell_cmd(
                    "ps -ef | grep appium | grep -v \"$$\" | awk  '{print \"kill -9 \" $2}' | sh")
                return False

        if self.driver is None:
            self.task_scheduler_failed("not init appium driver")
            return False

        if self.driver is None or self.target_device_name is None:
            self.task_scheduler_failed(
                "cureent env not right:["
                + str(self.driver) + ","
                + str(self.target_device_name) + "]")
            return False

        # 检查是否锁屏
        if utils_android.lock_off_screen_if_need(self.target_device_name) is False:
            self.task_scheduler_failed("---> lock_off_screen_if_need failed")
            return False
        return True

    def release_after_task(self):
        BaseTask.release_after_task(self)
        utils_logger.log("task_appium_base 释放资源")
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception:
                utils_logger.log("release_after_task caught failed")

    def is_in_target_page(self, target_page_file, compare_rule=100, retry_count=10,
                          interval_time=1):

        def wrapper(file):
            if os.path.exists(file):
                return file
            # 可能为相对路径
            abs_wrapper_file = os.path.abspath(
                project_root_path + "/tasks/appium/img/" + target_page_file)
            if os.path.exists(abs_wrapper_file):
                return abs_wrapper_file
            return None

        '''
        是否在指定页面
        :param target_page_file:
        :param compare_rule: 默认值为100，即两张图片的对比界限
        :return:
        '''
        wrapper_file = wrapper(target_page_file)
        if wrapper_file is None or os.path.exists(wrapper_file) is False:
            utils_logger.log("not fount target file for [" + str(target_page_file) + "]")
            return False
        # 重试对比
        if retry_count < 0:
            utils_logger.log(
                "---> is_in_target_page failed because no chance with:   " + target_page_file)
            return False
        # 获取target_file的file_name,不要后缀以及父目录相关
        shot_name = os.path.splitext(os.path.split(wrapper_file)[1])[0]
        scr_shot_pic = utils_appium.get_screen_shots(driver=self.driver,
                                                     target_device=self.target_device_name)
        if scr_shot_pic is not None and \
                utils_common.is_img_similary(file_first=wrapper_file, file_second=scr_shot_pic,
                                             hash_rule=compare_rule) is True:
            return True
        else:
            utils_logger.log("is_in_target_page sleep:", interval_time)
            time.sleep(interval_time)
            return self.is_in_target_page(target_page_file=target_page_file,
                                          compare_rule=compare_rule,
                                          retry_count=retry_count - 1, interval_time=interval_time)

    def get_query_str_by_desc(self, condent_desc):
        return "#content_desc#" + condent_desc

    def get_query_str_by_viewid(self, viewid):
        return "#viewid#" + str(viewid)

    def get_query_str_within_xpath_only_text(self, text, view_type='android.widget.TextView',
                                             attribute='text',
                                             is_force_match=True):
        "//android.widget.TextView[@text='***']"
        "//android.widget.TextView[contains(@text,'***')]"
        if is_force_match is True:
            return "//" + view_type + "[@" + attribute + "='" + text + "']"
        else:
            return "//" + view_type + "[contains(@" + attribute + ", '" + text + "')]"

    def __query_element(self, query_str):
        if query_str is None:
            utils_logger.log("not support this query with None protocal")
            return None
        utils_logger.log("[task_appium_base.__query_element] query:[" + str(query_str) + "]")
        '搜索element,以后有其他的情况，都可以在这里定义协议，以\'  # <协议标识>#的形式放在query_str的头部\''
        if query_str.startswith("#viewid#"):  # 针对可以拿到id的情况
            viewid = query_str.replace('#viewid#', '')  # strip('abc')表示会删除收尾的a、b、c字母，而不是只删除'abc'
            ele_viewid = utils_appium.find_element_by_viewid(self.driver, viewid=viewid)
            # if ele_viewid is None:
            #     utils_logger.log("not found element by find_element_by_viewid for " + str(viewid)
            return ele_viewid
        elif query_str.startswith("#content_desc#"):
            content_desc = query_str.strip('#content_desc#').strip()
            return utils_appium.find_element_by_content_desc(driver=self.driver,
                                                             content_desc=content_desc)
        else:
            return utils_appium.find_element_by_xpath(driver=self.driver, xpath=query_str)

    def except_case_in_query_ele(self):
        utils_logger.log("except_case_in_query_ele in BasicAppiumTask")
        '查询element的时候朋友的异常处理，True表示得以正常处理'
        # xpath模糊匹配速度太慢
        if self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('无响应', is_force_match=False),
                is_ignore_except_case=True, retry_count=0) is not None:
            # 检测到无响应
            if self.query_ele_wrapper(
                    self.get_query_str_within_xpath_only_text('等待',
                                                              view_type='android.widget.Button'),
                    click_mode='click', is_ignore_except_case=True, retry_count=0) is not None:
                return True
            else:
                self.task_scheduler_failed("检测到'无响应，但是无法关闭'")
        elif self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('打印纸未准备好', is_force_match=False),
                is_ignore_except_case=True, retry_count=0) is not None:
            if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('知道了'),
                                      click_mode='click', is_ignore_except_case=True,
                                      retry_count=0) is not None:
                return True
            else:
                self.task_scheduler_failed("检测到'打印纸未准备好，请检查！'文案，但无法关闭")
        elif self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text('平板仍存有残留目录和文件', is_force_match=False),
                is_ignore_except_case=True, retry_count=0) is not None:
            # 监测到删除应用历史残留文件
            if self.query_ele_wrapper(
                    self.get_query_str_within_xpath_only_text('立即删除',
                                                              view_type='android.widget.Button'),
                    click_mode='click', is_ignore_except_case=True, retry_count=0) is not None:
                return True
            else:
                utils_logger.log("监测到删除应用的历史残留数据弹框，但没办法关闭")
        return False

    def get_path_in_appium_img_dir(self, file_name):
        '返回file_name对应的全路径'
        return os.path.abspath(envs.get_appium_img_dir() + "/" + file_name)

    def query_ele_wrapper(self, query_str, is_ignore_except_case=False, click_mode=None,
                          retry_count=2,
                          time_wait_page_completely_resumed=0,
                          rect_scale_check_element_region=None):
        """

        :param query_str: 默认使用xpath方式搜索
        :param is_ignore_except_case: 是否忽略except_case_in_query_ele方法的调用
        :param click_mode: 事件响应模式，None：不响应，click:element.click(),position:tab方式
        :param retry_count: 加上首次执行的那次，总共会执行(retry_count+1)次
        :param time_wait_page_completely_resumed: 查询之前的延时：pre of query
        :param rect_scale_check_element_region:
        :return:
        """
        # TODO:添加element限制区域
        'query_ele_wrapper包装器'
        if query_str is None:
            utils_logger.log("query_ele_wrapper failed with no query_str:")
            return None
        # 屏蔽有时候页面还没有延迟刷新的问题
        if time_wait_page_completely_resumed > 0:
            # 该方法仅第一次执行是会被调用,递归中不执行
            utils_logger.log("query_ele_wrapper for sleep-time_wait_page_completely_resumed:",
                             time_wait_page_completely_resumed)
            time.sleep(time_wait_page_completely_resumed)
        query_res = self.__query_element(query_str=query_str)
        if query_res is not None:
            # 若找打的对象不为空的时候，还要判断找到的数据类型
            if isinstance(query_res, appium.webdriver.webelement.WebElement):
                if utils_appium.is_element_region_right_with_scale(element=query_res,
                                                                   device=self.target_device_name,
                                                                   region_rect_scale=rect_scale_check_element_region) is True:
                    query_ele_location = utils_appium.get_appium_element_position(query_res)
                    # 尝试捕获click事件
                    if click_mode is not None:
                        try:
                            del self.upload_files[:]
                            if click_mode == 'position' and query_ele_location is not None:
                                utils_logger.log("[query_ele_wrapper] 基于坐标响应单击事件")
                                if self.safe_tap_in_point(
                                        point=(
                                                query_ele_location['x'],
                                                query_ele_location['y'])) is False:
                                    self.task_scheduler_failed('safe_tap_in_point failed')
                                    return None
                            elif click_mode == 'click':
                                # 只有当click_mode是"position"且坐标可用时使用tab方式，其他默认使用element.click()方式
                                utils_logger.log("[query_ele_wrapper] 基于element.click()响应单击事件")
                                query_res.click()
                            else:
                                raise Exception(
                                    '[query_ele_wrapper]unknown click_mode:' + click_mode)
                            utils_logger.log("[query_ele_wrapper] click for element:[",
                                             query_res,
                                             "] with location:", query_ele_location)
                            return query_res
                        except Exception as e:
                            utils_logger.log("try to click failed ", e.message)
                            utils_logger.log(traceback.format_exc())
                    else:
                        utils_logger.log("[query_ele_wrapper] location:", query_ele_location)
                        return query_res
                else:
                    utils_logger.log(
                        "--->[query_ele_wrapper.is_element_region_right_with_scale] 校验element坐标失败，启用重试机制")
            else:
                utils_logger.log("unsupport type of element: ", type(query_res))
        utils_logger.log("--- >[task_appium_base.query_ele_wrapper]", query_str,
                         " with retry_count:", retry_count)
        # 若上面的判断逻辑失败，则表示还没有找到'可用'的element
        period_checked = 0.2
        utils_logger.log("query_ele_wrapper sleep:", period_checked)
        time.sleep(period_checked)  # 500毫秒重复执行一次
        if is_ignore_except_case is False and self.except_case_in_query_ele() is True:
            # except_case_in_query_ele为True表示处理生效
            return self.query_ele_wrapper(query_str=query_str,
                                          is_ignore_except_case=is_ignore_except_case,
                                          click_mode=click_mode,
                                          retry_count=retry_count,
                                          time_wait_page_completely_resumed=0,
                                          rect_scale_check_element_region=rect_scale_check_element_region)
        else:
            # 若第一次检测失败，至少尝试使用except_case_in_query_ele检测下，若也失败再检测剩下的重试次数
            if retry_count <= 0:
                return None
            else:
                return self.query_ele_wrapper(query_str=query_str,
                                              is_ignore_except_case=is_ignore_except_case,
                                              click_mode=click_mode,
                                              retry_count=retry_count - 1,
                                              time_wait_page_completely_resumed=0,
                                              rect_scale_check_element_region=rect_scale_check_element_region)

    def query_point_size_within_text(self, search_text, retry_count=2, interval_time=5,
                                     cutted_rect=None,
                                     is_ignore_except_case=False, is_check_view_inflated=True):
        points = self._query_points_with_text_by_ocr(search_text=search_text,
                                                     retry_count=retry_count,
                                                     interval_time=interval_time,
                                                     cutted_rect=cutted_rect,
                                                     is_ignore_except_case=is_ignore_except_case,
                                                     is_check_view_inflated=is_check_view_inflated)
        if points is None:
            utils_logger.log("未找到可用元素")
            return 0
        return len(points)

    def wait_view_layout_finish(self, is_check_view_inflated=True):
        """
        等待页面绘制完成
        @:return <页面是否绘制完成，屏幕截图>
        """
        file_screen_shot = utils_appium.get_screen_shots(driver=self.driver,
                                                         target_device=self.target_device_name)
        if is_check_view_inflated is False:
            utils_logger.log("[wait_view_layout_finish] 不需要检查当前页面是否加载完")
            return True, file_screen_shot
        # 使用图片空白区域识别页面是否加载完成
        is_view_layout_finished = False
        for check_index in range(20):  # 最多重试20次，每次时间间隔为1秒
            # 基于图片识别纯色图片范围判断页面是否加载完成
            if file_screen_shot is None or utils_android.is_page_loging(file_screen_shot) is True:
                utils_logger.log("[wait_view_layout_finish] sleep util is_page_loging true:",
                                 check_index)
                time.sleep(1)
                file_screen_shot = utils_appium.get_screen_shots(driver=self.driver,
                                                                 target_device=self.target_device_name)
            else:
                is_view_layout_finished = True
                break
        return is_view_layout_finished, file_screen_shot

    def safe_touch_action(self, tab_interval, retry_count=3, is_down=True, tab_center=0.5,
                          duration=300):
        """
        :param tab_interval: 触摸区间
        :param retry_count: 重试次数
        :param is_down: 是否是垂直方向移动
        :param tab_center:
        :param duration: 耗时
        :return:
        """
        try:
            utils_logger.log("safe_touch_action with retry_count:", retry_count)
            utils_appium.touch_action(driver=self.driver,
                                      target_device_name=self.target_device_name, is_down=is_down,
                                      tab_center=tab_center, tab_interval=tab_interval,
                                      duration=duration)
            return True
        except Exception as exception:
            except_name = exception.__class__.__name__
            # 屏蔽
            if retry_count <= 0 or except_name == "InvalidSessionIdException":
                utils_logger.log('TouchError:safe_touch_action caught exception')
                return False
            else:
                return self.safe_touch_action(tab_interval=tab_interval,
                                              retry_count=retry_count - 1, is_down=is_down,
                                              tab_center=tab_center, duration=duration)

    def safe_tap_in_point(self, point, retry_count=3):
        """tap_in_point安全模式"""
        try:
            utils_logger.log("safe_tap_in_point with retry_count:", retry_count)
            utils_appium.tap_in_point(self.driver, point)
            return True
        except:
            if retry_count <= 0:
                return False
            else:
                return self.safe_tap_in_point(point=point, retry_count=retry_count - 1)

    def _query_points_with_text_by_ocr(self, search_text, retry_count=2, interval_time=5,
                                       cutted_rect=None,
                                       is_ignore_except_case=False, is_check_view_inflated=True):
        """
        Desc:根据正则匹配搜索文字在图片中的位置
        :param search_text:
        :param retry_count:
        :param interval_time: 重试时间间隔：由于_query_points_with_text_by_ocr方法一般应用于webview，因此适当延长间隔周期
        :param cutted_rect: 裁剪比例,[横向-start,横向-end,竖向-start,竖向-end]
        :param is_ignore_except_case:
        :param is_check_view_inflated:
        :return:
        """
        utils_logger.log(
            "--->[_query_points_with_text_by_ocr] '" + search_text + "' with retry_count:" + str(
                retry_count))
        # 检测页面是否加载完成
        is_view_layout_finished, file_screen_shot = self.wait_view_layout_finish(
            is_check_view_inflated)
        if is_view_layout_finished is False:
            utils_logger.log("[_query_points_with_text_by_ocr] 页面在指定时间并没有加载完成")
            self.task_scheduler_failed(
                "[_query_points_with_text_by_ocr] '" + search_text + "' 页面在指定时间并没有加载完成")
            return None
        if file_screen_shot is None:
            self.task_scheduler_failed(
                "[_query_points_with_text_by_ocr] '" + search_text + "' failed because no file_screen_shot")
            return None
        # 根据参数裁剪图片
        cutted_file_screen_shot = file_screen_shot
        if cutted_rect is not None:
            # 将裁剪比例转化为具体坐标
            rect_formted = image_utils.get_rect_formated(raw_file_path=file_screen_shot,
                                                         cutted_scale=cutted_rect)
            cutted_file_screen_shot = image_utils.cutted_image(raw_file_path=file_screen_shot,
                                                               rect_formted=rect_formted,
                                                               cutted_save_file_path=file_utils.generate_suffix_file(
                                                                   file_screen_shot,
                                                                   suffix="cutted"))
        if cutted_file_screen_shot is None:
            utils_logger.log(
                "--->[_query_points_with_text_by_ocr] '" + search_text + "' 截图文件裁剪 failed")
            self.task_scheduler_failed(
                '[_query_points_with_text_by_ocr] create cutted image for screen shot failed')
            return None
        # 检查匹配元素
        match_points = ocr_utils.get_points_within_text(cutted_file_screen_shot, search_text)
        if match_points is not None and len(match_points) > 0:
            # 修饰元素
            if cutted_rect is None:
                return match_points
            else:
                utils_logger.log(
                    "--->[_query_points_with_text_by_ocr] '" + search_text + "' match_points:",
                    match_points)
                for match_point_item in match_points:
                    match_point_item['avaiable_point'] = (
                        match_point_item['avaiable_point'][0] + rect_formted[0],
                        match_point_item['avaiable_point'][1] + rect_formted[1])
                utils_logger.log(
                    "--->[_query_points_with_text_by_ocr] '" + search_text + "' match_points after format:",
                    match_points)
                return match_points
        else:
            # 开启重试
            if retry_count <= 0:
                utils_logger.log(
                    "--->[_query_points_with_text_by_ocr] '" + search_text + "' failed because no chance")
                return None
            else:
                utils_logger.log(
                    "--->[_query_points_with_text_by_ocr] '" + search_text + "' with retry_count:",
                    retry_count, " ,sleep for :", interval_time)
                time.sleep(interval_time)
                if is_ignore_except_case is False and self.except_case_in_query_ele() is True:
                    # 指可能有其他外界因素打断此次查询
                    return self._query_points_with_text_by_ocr(search_text=search_text,
                                                               retry_count=retry_count,
                                                               interval_time=interval_time,
                                                               cutted_rect=cutted_rect,
                                                               is_ignore_except_case=is_ignore_except_case,
                                                               is_check_view_inflated=is_check_view_inflated)
                else:
                    return self._query_points_with_text_by_ocr(search_text=search_text,
                                                               retry_count=retry_count - 1,
                                                               interval_time=interval_time,
                                                               cutted_rect=cutted_rect,
                                                               is_ignore_except_case=is_ignore_except_case,
                                                               is_check_view_inflated=is_check_view_inflated)

    def query_only_point_within_text(self, search_text, retry_count=2, interval_time=5,
                                     is_auto_click=False,
                                     cutted_rect=None,
                                     is_ignore_except_case=False, is_check_view_inflated=True,
                                     is_output_event_tract=False):
        """
        :param search_text: 搜索文案，支持正则匹配
        :param retry_count:
        :param interval_time:
        :param is_auto_click:
        :param cutted_rect:
        :param is_ignore_except_case:
        :param is_check_view_inflated:
        :param is_output_event_tract 是否输出事件跟踪信息
        :return:
        """
        points = self._query_points_with_text_by_ocr(search_text=search_text,
                                                     retry_count=retry_count,
                                                     interval_time=interval_time,
                                                     cutted_rect=cutted_rect,
                                                     is_ignore_except_case=is_ignore_except_case,
                                                     is_check_view_inflated=is_check_view_inflated)
        if points is None or len(points) == 0:
            utils_logger.log("未找到可用元素")
            return None
        else:
            if len(points) > 1:
                utils_logger.log("查询元素不唯一，请检查页面元素")
                self.task_scheduler_failed(
                    ("query_only_point_within_text[" + search_text + "]元素不唯一: ").joins(points))
                return None
            else:
                single_point = points[0]
                if is_auto_click is True:
                    utils_logger.log("auto query_only_point_within_text for " + search_text)
                    del self.upload_files[:]
                    if is_output_event_tract is True:
                        self.write_screen_shot_into_file(suffix='ocr_start')
                        self.write_page_resource_into_file(suffix='ocr_start')
                    if self.safe_tap_in_point(single_point['avaiable_point']) is False:
                        self.task_scheduler_failed('safe_tap_in_point failed')
                        return None
                    if is_output_event_tract is True:
                        self.write_screen_shot_into_file(suffix='ocr_end')
                        self.write_page_resource_into_file(suffix='ocr_end')
                return single_point

    def _query_part_image_matchs(self, part_pic_path, part_rect_scale):
        """查询所有在截图中满足条件的子图位置"""
        if os.path.exists(part_pic_path) is False:
            part_pic_path = os.path.abspath(
                project_root_path + "/tasks/appium/img/" + part_pic_path)
        utils_logger.log("query_point_throw_part_pic:", part_pic_path)
        # 检测页面是否加载完成
        is_view_layout_finished, file_screen_shot = self.wait_view_layout_finish()
        if is_view_layout_finished is False:
            utils_logger.log("[query_point_throw_part_pic] 页面在指定时间并没有加载完成")
            self.task_scheduler_failed(
                "[query_point_throw_part_pic] '" + part_pic_path + "' 页面在指定时间并没有加载完成")
            return None
        if file_screen_shot is None:
            self.task_scheduler_failed(
                "[query_point_throw_part_pic] '" + part_pic_path + "' failed because no file_screen_shot")
            return None
        # 裁剪获得比对的资源图片
        utils_logger.log("[query_point_throw_part_pic] 格式化资源文件")
        cutted_file_path = image_utils.cutted_image_with_scale(raw_file_path=part_pic_path,
                                                               cutted_rect_scale=part_rect_scale,
                                                               cutted_save_file_path=file_utils.generate_suffix_file(
                                                                   part_pic_path,
                                                                   save_to_dir=envs.get_out_dir(),
                                                                   suffix="cutted"))
        child_template = Template(cutted_file_path)
        # cutted_file_path与当前截图比对:其中根据check_rect_scale裁剪截图
        utils_logger.log("[query_point_throw_part_pic] 格式化截图")
        parent_template = Template(image_utils.cutted_image_with_scale(file_screen_shot))
        return child_template.find_all_matchs(parent_template)

    def query_only_match_part_with_click(self, part_pic_path, part_rect_scale,
                                         is_ignore_except_case=False,
                                         is_auto_click=False):
        """针对子图仅搜索到一个结果并执行自动点击"""
        results_mathched_within_check_region = self._query_matchs_within_check_region(
            part_pic_path=part_pic_path,
            part_rect_scale=part_rect_scale,
            is_ignore_except_case=is_ignore_except_case)
        click_match_point = None
        # TODO:这里还需要校验是否只存在一个搜索结果
        if results_mathched_within_check_region is not None and len(
                results_mathched_within_check_region) > 0:
            if is_auto_click:
                click_match_point = results_mathched_within_check_region[0]['result']
                utils_logger.log("[query_only_match_part_with_click] 检索到需要自动点击:",
                                 click_match_point)
                del self.upload_files[:]
                # self.write_page_resource_into_file(suffix='aircv_start')
                # self.write_screen_shot_into_file(suffix='aircv_start')
                if self.safe_tap_in_point(click_match_point) is False:
                    self.task_scheduler_failed('safe_tap_in_point failed')
                    return None
                # self.write_page_resource_into_file(suffix='aircv_end')
                # self.write_screen_shot_into_file(suffix='aircv_end')
        return click_match_point

    def _query_matchs_within_check_region(self, part_pic_path, part_rect_scale,
                                          check_rect_scale=[0, 1, 0, 1],
                                          is_ignore_except_case=False, retry_count=2):
        """
        根据子图搜索截图里所有满足条件的区域，包含重试,需要对搜索的对应子图位置做check
        :param is_ignore_except_case:
        :param part_pic_path 子图原始图片
        :param part_rect_scale 原始图片中待比对的区域，用于裁剪子图原始图片以得到待比对子图
        :param check_rect_scale 检查最终搜索结果是否在限定区域内,[left,right,top,bottom]
        :param retry_count:重试次数
        """
        checked_region_matchs = []
        query_matchs = self._query_part_image_matchs(part_pic_path=part_pic_path,
                                                     part_rect_scale=part_rect_scale)
        if query_matchs is not None:
            for match_item in query_matchs:
                # 这里检查每个子图的位置是否合法
                utils_logger.log("[query_matchs_within_check_region] start to check region:",
                                 match_item)
                checked_region_matchs.append(match_item)
        # 重试机制
        if checked_region_matchs is None or len(checked_region_matchs) == 0:
            if retry_count <= 0:
                utils_logger.log("[query_matchs_within_check_region] failed with no chance")
                return None
            utils_logger.log("[query_matchs_within_check_region] 未找到相应元素，启动重试：", retry_count)
            if is_ignore_except_case is False and self.except_case_in_query_ele() is True:
                return self.query_matchs_within_check_region(part_pic_path=part_pic_path,
                                                             part_rect_scale=part_rect_scale,
                                                             check_rect_scale=check_rect_scale,
                                                             is_ignore_except_case=is_ignore_except_case,
                                                             retry_count=retry_count)
            else:
                return self.query_matchs_within_check_region(part_pic_path=part_pic_path,
                                                             part_rect_scale=part_rect_scale,
                                                             check_rect_scale=check_rect_scale,
                                                             is_ignore_except_case=is_ignore_except_case,
                                                             retry_count=retry_count - 1)
        else:
            utils_logger.log("query_matchs_within_check_region:", checked_region_matchs)
            return checked_region_matchs
