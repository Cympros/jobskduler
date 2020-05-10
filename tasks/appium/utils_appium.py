# coding=utf-8

# appium相关工具类
from appium import webdriver as appium_webdriver
import os
import sys
import time
import traceback

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../')
sys.path.append(project_root_path)

from helper import utils_common, utils_logger
# from helper import envs
from helper import utils_android


def get_appium_element_position(element):
    """获取元素位置"""
    if element is None:
        return None
    try:
        ele_position = element.location
        utils_logger.log("[get_appium_element_position]", ele_position)
        return ele_position
    except Exception:
        utils_logger.log(traceback.format_exc())
    return None


def is_element_region_right_with_scale(element, device, region_rect_scale=None):
    utils_logger.log("is_element_region_right_with_scale calling...")
    region_rect = None
    if region_rect_scale is not None:
        resolution = utils_android.get_resolution_by_device(device).split('x')
        left = int(float(resolution[0]) * region_rect_scale[0])
        right = int(float(resolution[0]) * region_rect_scale[1])
        top = int(float(resolution[1]) * region_rect_scale[2])
        bottom = int(float(resolution[1]) * region_rect_scale[3])
        region_rect = (left, right, top, bottom)
    return is_element_region_right(element=element, region_rect=region_rect)


def is_element_region_right(element, region_rect=None):
    """
    判断元素是否在指定区域
    :param element: 
    :param device: 
    :param region_rect: (left,right,top,bottom),以具体坐标显示
    :return: 
    """
    if region_rect is None:
        # 为什么为空时，不构造[0,1,0,1]的默认值？  因为有时候有些情况下比如浮框类似的，坐标并不是理想中的样子
        utils_logger.log("[is_element_region_right] 待校验区域为空，因此认为搜索的element在屏幕内")
        return True
    utils_logger.log("[is_element_region_right] 校验元素是否在指定区域")
    ele_location = get_appium_element_position(element)
    if ele_location is None:
        utils_logger.log("[is_element_region_right] 当前元素获取location失败,则认为元素可见")
        return True
    utils_logger.log("[is_element_region_right] region_rect:", region_rect)
    utils_logger.log("[is_element_region_right] ele_location:", ele_location)
    if region_rect[0] <= int(ele_location['x']) <= region_rect[1] and region_rect[2] <= int(
            ele_location['y']) <= \
            region_rect[3]:
        utils_logger.log("[is_element_region_right] 元素区域校验 success")
        return True
    else:
        utils_logger.log("[is_element_region_right] 元素区域校验 failed")
        return False


def touch_action(driver, target_device_name, is_down=True, tab_center=0.5, tab_interval=[0, 1],
                 duration=300):
    '''
    :param driver: 
    :param target_device_name: 
    :param is_down: 
    :param tab_center: 
    :param tab_interval: 从0-1，亦可1-0
    :param duration: 滑动的时长
    :return: 
    '''
    utils_logger.log("[touch_action] tab_interval=", tab_interval, ",is_down=", is_down,
                     ",tab_center", tab_center)
    'TODO：Peform Action的使用'
    resolution = utils_android.get_resolution_by_device(target_device_name).split('x')
    screen_width = float(resolution[0])
    screen_heigh = float(resolution[1])
    if is_down:
        # utils_logger.log("touch_action:","上下滑动"
        t_tab_center = int(tab_center * screen_width)
        t_from = int(float(tab_interval[0]) * screen_heigh)
        t_to = int(float(tab_interval[1]) * screen_heigh)
        driver.swipe(t_tab_center, t_from, tab_center, t_to, duration)
    else:
        # utils_logger.log("touch_action:","左右滑动"
        t_tab_center = int(tab_center * screen_heigh)
        t_from = int(float(tab_interval[0]) * screen_width)
        t_to = int(float(tab_interval[1]) * screen_width)
        utils_logger.log("[touch_action] t_tab_center:", t_tab_center, ",t_from:", t_from,
                         ",t_to:", t_to)
        driver.swipe(t_from, t_tab_center, t_to, t_tab_center, duration)


def start_appium_service(device, appium_port, access_appium_bp_port, retry_count=5,
                         interval_time=5):
    '''启动appium服务,添加重试机制'''
    utils_logger.log("check_appium_service_state with retry_count:    ",
                     retry_count)
    # 存在appium进程则输出success，否则输出空串
    appium_state_check_cmd = "ps -ef | grep \'appium"
    if appium_port is not None:
        appium_state_check_cmd += " -p " + str(appium_port)
    appium_state_check_cmd += "\' | grep -v \'grep\' >/dev/null && echo success"

    # 检测appium是否安装
    check_res, check_error = utils_common.exec_shell_cmd('which appium')
    if check_error is not None:
        utils_logger.log("appium服务还未安装,调用'npm install -g appium'执行安装程序")
        return False
    # 屏蔽因日志太多堵塞
    appium_start_cmd = "nohup appium "
    if appium_port is not None:
        appium_start_cmd += " -p " + str(appium_port)
    if access_appium_bp_port is not None:
        appium_start_cmd += " -bp " + str(access_appium_bp_port)
    if device is not None:
        appium_start_cmd += " -U " + str(device)
    appium_start_cmd += " 1>/dev/null 2>&1 & "

    res_apm, res_apm_error = utils_common.exec_shell_cmd(appium_state_check_cmd)
    utils_logger.log(" appium服务是否启动", "[" + appium_state_check_cmd + "]",
                     "[" + str(res_apm) + "]", "[" + str(res_apm_error) + "]")
    if res_apm is not None:
        return True
    else:
        # 启动appium服务
        res, err = utils_common.exec_shell_cmd(appium_start_cmd)
        utils_logger.log("#start_appium_service# sleep:[" + str(interval_time) + "],[" + str(
            appium_start_cmd) + "]",
                         "[" + str(res) + "]", "[" + str(err) + "]")
        time.sleep(interval_time)  # 等待appium服务完全启动
        return False if retry_count <= 0 else start_appium_service(device, appium_port,
                                                                   access_appium_bp_port,
                                                                   retry_count=retry_count - 1,
                                                                   interval_time=interval_time)


def tap_in_point(driver, point, delay_to_load=0):
    '点击页面指定区域,delay_to_load默认为3秒'
    if point is None:
        utils_logger.log("methood of tap_in_point canot fount point")
        return
    tab_x = point[0]
    tab_y = point[1]
    if delay_to_load > 0:
        utils_logger.log("tap_in_point sleep:", delay_to_load)
        time.sleep(delay_to_load)
    utils_logger.log("tap_in_point: [" + str(tab_x) + "," + str(tab_y) + "]")
    driver.tap([(tab_x, tab_y)], 2)


def get_screen_shots(driver, target_device, file_path=None, retry_count=2):
    """
    获取当前截图
    :param driver: 
    :param target_device: 
    :param file_path: 截图存储位置
    :param retry_count: 
    :return: 
    """
    if driver is None:
        utils_logger.log("failed with no driver")
        return None
    utils_logger.log("[get_screen_shots] screen shot with retry count:", retry_count)
    if file_path is None:
        utils_logger.log("[get_screen_shots] 构建默认截图存储路径")
        resolution_within_devices = utils_android.get_resolution_by_device(device=target_device)
        file_name = "screen_tmp_" + \
                    (resolution_within_devices if resolution_within_devices is not None else "none") \
                    + ".png"
        file_path = os.path.abspath(envs.get_out_dir() + file_name)
        # 删除缓存
    if os.path.exists(file_path):
        utils_logger.log("get_screen_shots clear cache for file: ", file_path)
        os.remove(file_path)
    try:
        driver.get_screenshot_as_file(file_path)
        return file_path
    except Exception as exception:
        except_name = exception.__class__.__name__  # exception的名称
        utils_logger.log("[get_screen_shots] caught exception:", retry_count)
        if retry_count > 0 and except_name != "InvalidSessionIdException":
            return get_screen_shots(driver=driver, target_device=target_device, file_path=file_path,
                                    retry_count=retry_count - 1)
        else:
            utils_logger.log(traceback.format_exc())
            return None


def get_pg_source(driver, retry_count=5):
    if driver is None:
        utils_logger.log('failed because driver is null')
        return None
    utils_logger.log("get_pg_source with retry_count:", retry_count)
    try:
        return driver.page_source
    except Exception:
        if retry_count <= 0:
            return None
        else:
            time.sleep(1)
            return get_pg_source(driver=driver, retry_count=retry_count - 1)


def write_page_resource(driver, file_page_resource=None):
    '''
    desc:把pagr-resource文件写入文件
    :param driver: 
    :param file_page_resource: such as file_page_resource=envs.get_out_dir()+"page_resource.txt"
    :return: 写入的文件路径，写入失败时返回None
    '''
    if file_page_resource is None:
        utils_logger.log("无文件用于写入，直接退出")
        return None
    pgres = get_pg_source(driver)
    if pgres is None:
        return None
    with open(file_page_resource, 'w') as f:
        f.write(pgres)
    return file_page_resource


def get_cur_act(driver, delay_time=0):
    if driver is None:
        utils_logger.log("failed because driver is null")
        return None
    if delay_time > 0:
        utils_logger.log("get_cur_act sleep:", delay_time)
        time.sleep(delay_time)
    try:
        return driver.current_activity
    except Exception:
        utils_logger.log("get_cur_act caught exception:", traceback.format_exc())
        return None


def find_element_by_content_desc(driver, content_desc, retry_count=2, interval_time=0.1):
    '查询content-desc字段'
    utils_logger.log("find_element_by_content_desc[\"" + content_desc + "\"] with retry_count:",
                     retry_count)
    element = None
    try:
        element = driver.find_element_by_accessibility_id(content_desc)
    finally:
        if element is not None:
            return element
        elif retry_count <= 0:
            utils_logger.log(
                "find_element_by_content_desc[" + content_desc + "] failed with no chance")
            return None
        else:
            utils_logger.log("find_element_by_content_desc sleep:", interval_time)
            time.sleep(interval_time)
            return find_element_by_content_desc(driver, content_desc, retry_count - 1,
                                                interval_time)


def find_element_by_viewid(driver, viewid, retry_count=2, interval_time=0.1):
    return None
    # '根据id寻找资源'
    # utils_logger.log("find_element_by_viewid with viewid:[" + viewid + "] with retry_count:", retry_count)
    # element = None
    # try:
    #     element = driver.find_element_by_id(viewid)
    # finally:
    #     if element is not None:
    #         return element
    #     elif retry_count <= 0:
    #         utils_logger.log("find_element_by_viewid[" + viewid + "] failed with no chance")
    #         return None
    #     else:
    #         utils_logger.log("find_element_by_viewid sleep:", interval_time)
    #         time.sleep(interval_time)
    #         return find_element_by_viewid(driver=driver, viewid=viewid, retry_count=retry_count - 1,
    #                                       interval_time=interval_time)


def find_element_by_xpath(driver, xpath, retry_count=2, interval_time=0.1):
    '基于xpath寻找控件'
    utils_logger.log("find_element_by_xpath[" + xpath + "] with retry_count:", retry_count)
    element = None
    try:
        element = driver.find_element_by_xpath(xpath)
    finally:
        if element is not None:
            utils_logger.log("find_element_by_xpath with xpath", xpath)
            return element
        elif retry_count <= 0:
            utils_logger.log("find_element_by_xpath：[" + xpath + "] failed with no chance")
            return None
        else:
            utils_logger.log("find_element_by_xpath sleep:", interval_time)
            time.sleep(interval_time)
            return find_element_by_xpath(driver=driver, xpath=xpath, retry_count=retry_count - 1,
                                         interval_time=interval_time)


def wait_activity_with_status(driver, target, check_period=1, retry_count=10):
    '''
    :param retry_count: 重试次数
    :param target: 待匹配的界面，支持单个字串以及数组
    :param check_period:轮训周期，单位为秒
    :return:
    '''

    def is_in_fliter(lists, search_fliter):
        if search_fliter is None or lists is None:
            return False

        search_status = False
        utils_logger.log(
            "wait_activity_with_status.is_in_fliter<" + search_fliter + "> in <" + str(lists) + ">")
        for item in lists:
            if item.endswith(search_fliter):
                search_status = True
                break
        return search_status

    '''
    等待activity响应
    :param driver:
    :param target_act: 目标activity
    :param check_period: 检测周期，默认2秒
    :param check_count: 总共检测次数
    :return:
    '''
    res_status = False
    # 格式化搜索条件
    if not isinstance(target, list):
        fliters = [target]
    else:
        fliters = target
    count = 0
    while count < retry_count:
        if is_in_fliter(fliters, get_cur_act(driver=driver)):
            res_status = True
            break
        count = count + 1
        if count >= retry_count:
            break
        else:
            utils_logger.log("wait_activity_with_status sleep:", check_period)
            time.sleep(check_period)
    return res_status


def get_driver_by_launch_app(application_id, launch_activity, device_name_to_connected,
                             is_need_setting_input_manager,
                             appium_port, access_appium_bp_port):
    """
    启动待测试apk并返回driver对象
    :param access_appium_bp_port:
    :param appium_port: appium服务端口
    :param application_id:
    :param launch_activity: 
    :param device_name_to_connected: 
    :param is_need_setting_input_manager: 是否需要添加appium输入法支持
    :return: 
    """
    if application_id is None:
        return None
    if launch_activity is None:
        cmd = "adb shell dumpsys activity | grep -v bnds | grep 'android.intent.category.LAUNCHER'  " \
              + " | grep '" + application_id + "'"
        utils_logger.log("#get_driver_by_launch_app# 打开应用，并执行\"" + cmd + "\"获取启动activity")
        return None

    # 判断appium服务是否启动
    if start_appium_service(device_name_to_connected, appium_port, access_appium_bp_port) is False:
        utils_logger.log(
            "#get_driver_by_launch_app# start_appium_service失败[端口信息]：" + str(appium_port))
        return None

    platform_version = utils_android.get_deivce_android_version(device=device_name_to_connected)
    desired_caps = {'platformName': 'Android',
                    'platformVersion': platform_version,
                    'deviceName': device_name_to_connected,
                    'uuid': utils_android.get_device_tag(device_name_to_connected),
                    'noReset': True,
                    'appPackage': application_id,
                    'appActivity': launch_activity,
                    # 'chromeOptions':{'androidProcess': 'com.tencent.mm:tools'},   # 该语句非必须
                    'newCommandTimeout': 3 * 60,  # 无响应再关闭
                    # 'automationName':'uiautomator2'   # todo:还不稳定，观望中
                    }
    if is_need_setting_input_manager is True:
        # 下面两项用于使键盘支持中文输入
        desired_caps['unicodeKeyboard'] = True
        desired_caps['resetKeyboard'] = True
    utils_logger.log('#get_driver_by_launch_app#', desired_caps, appium_port)
    driver = appium_webdriver.Remote("http://127.0.0.1:" + str(appium_port) + '/wd/hub',
                                     desired_caps)
    # driver.implicitly_wait(10)  # 设置全局隐性等待时间，单位秒
    return driver


if __name__ == '__main__':
    pass