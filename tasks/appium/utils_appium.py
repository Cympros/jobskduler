# coding=utf-8

# appium相关工具类
import re
import socket
import threading

from appium import webdriver as appium_webdriver
import os
import sys
import time
import traceback

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../')
sys.path.insert(0, project_root_path)

from helper import utils_common, utils_logger
from helper import utils_android


def get_appium_element_position(element):
    """获取元素位置
    @return 结果类似:{'x': 870, 'y': 1692}
    """
    if element is None:
        return None
    # 先基于bounds解析中间位置
    try:
        utils_logger.debug("get_attribute('clickable')", element.get_attribute("clickable"))
        bounds_attr = element.get_attribute("bounds")
        utils_logger.debug("get_attribute('bounds')", bounds_attr)
        # 解析结果: [870,1692][1063,1912]
        location_array = re.split('\[|,|\]', bounds_attr)
        return {'x': (int(location_array[1]) + int(location_array[4])) / 2,
                'y': (int(location_array[2]) + int(location_array[5])) / 2}
    except Exception as e:
        utils_logger.log(e, traceback.format_exc())
    # 使用element自带的位置
    try:
        ele_position = element.location
        utils_logger.debug("element.location获取的位置", ele_position)
        return ele_position
    except Exception as e:
        utils_logger.log(e, traceback.format_exc())
    return None


def is_element_region_right_with_scale(element, device, region_rect_scale=None):
    # utils_logger.log("is_element_region_right_with_scale calling...")
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
        utils_logger.debug("待校验区域为空，因此认为搜索的element在屏幕内")
        return True
    ele_location = get_appium_element_position(element)
    if ele_location is None:
        utils_logger.debug("当前元素获取location失败,则认为元素可见")
        return True
    utils_logger.debug("region_rect:", region_rect)
    utils_logger.debug("ele_location:", ele_location)
    if region_rect[0] <= int(ele_location['x']) <= region_rect[1] and region_rect[2] <= int(
            ele_location['y']) <= \
            region_rect[3]:
        utils_logger.debug("元素区域校验 success")
        return True
    else:
        utils_logger.debug("元素区域校验 failed")
        return False


def scroll_by(driver, target_device_name, is_down=True, tab_center=0.5, tab_interval=[0, 1],
              duration=100):
    """
    :param driver:
    :param target_device_name:
    :param is_down:
    :param tab_center:
    :param tab_interval: 从0-1，亦可1-0
    :param duration: 滑动的时长
    :return:
    """
    utils_logger.debug("tab_interval=%s,is_down=%s,tab_center=%s" % (str(tab_interval), str(is_down), str(tab_center)))
    'TODO：Peform Action的使用'
    resolution_str_by_device = utils_android.get_resolution_by_device(target_device_name)
    if resolution_str_by_device is None:
        utils_logger.log("读取设备分辨率失败")
        return
    resolution = resolution_str_by_device.split('x')
    screen_width = float(resolution[0])
    screen_heigh = float(resolution[1])
    time.sleep(1)  # driver.swipe经常崩溃,添加延时任务
    if is_down:
        utils_logger.debug("scroll_by:", "上下滑动")
        t_tab_center = int(tab_center * screen_width)
        t_from = int(float(tab_interval[0]) * screen_heigh)
        t_to = int(float(tab_interval[1]) * screen_heigh)
        driver.swipe(t_tab_center, t_from, tab_center, t_to, duration)
    else:
        utils_logger.debug("scroll_by:", "左右滑动")
        t_tab_center = int(tab_center * screen_heigh)
        t_from = int(float(tab_interval[0]) * screen_width)
        t_to = int(float(tab_interval[1]) * screen_width)
        utils_logger.log("[scroll_by] t_tab_center:", t_tab_center, ",t_from:", t_from,
                         ",t_to:", t_to)
        driver.swipe(t_from, t_tab_center, t_to, t_tab_center, duration)


def start_appium_service(device, appium_port, access_appium_bp_port, appium_server_log, retry_count=5, interval_time=5):
    """启动appium服务,添加重试机制"""
    # 检测appium是否安装
    check_res, check_error = utils_common.exec_shell_cmd('which appium')
    if not check_res:  # 空串表示未安装appium服务
        utils_logger.log("appium服务还未安装,调用'npm install -g appium'执行安装程序")
        return False
    # utils_logger.debug("appium服务安装地址", check_res)
    utils_logger.debug("重试检查appium服务启动状态 ", retry_count)
    if appium_port is None or access_appium_bp_port is None or device is None:
        utils_logger.debug("参数异常", appium_port, access_appium_bp_port, device)
        return False
    appium_start_cmd = "appium -p %s -bp %s -U %s" % (str(appium_port), str(access_appium_bp_port), str(device))
    # 存在appium进程
    appium_state_check_cmd = "ps -ef | grep '%s' | grep -v 'grep'" % appium_start_cmd
    res_apm, res_apm_error = utils_common.exec_shell_cmd(appium_state_check_cmd)
    # utils_logger.debug("appium服务是否启动", appium_state_check_cmd, str(res_apm), str(res_apm_error))
    if res_apm is not None:
        return True
    else:
        utils_logger.debug("关闭appium服务占用",
                           utils_common.exec_shell_cmd("ps -ef | grep '\-U %s'| grep -v 'grep'" % str(device)))
        # 关闭appium服务,保证同一时刻同一个设备仅有唯一appium服务
        utils_common.exec_shell_cmd(
            "ps -ef | grep '%s*io.appium.uiautomator2.server.test/androidx.test.runner.AndroidJUnitRunner'| grep -v 'grep' | awk '{print \"kill -9 \" $2}' | sh" % str(
                device))
        utils_common.exec_shell_cmd(
            "ps -ef | grep '\-U %s'| grep -v 'grep' | awk '{print \"kill -9 \" $2}' | sh" % str(device))
        res, err = utils_common.exec_shell_cmd("nohup %s >>%s 2>&1 &" % (appium_start_cmd, appium_server_log))
        if interval_time > 0:
            utils_logger.debug("sleep %s to exec command [%s] with response:[%s] and error:[%s]" %
                               (str(interval_time), str(appium_start_cmd), str(res), str(err)))
            time.sleep(interval_time)  # 等待appium服务完全启动
        return False if retry_count <= 0 else start_appium_service(device=device,
                                                                   appium_port=appium_port,
                                                                   access_appium_bp_port=access_appium_bp_port,
                                                                   appium_server_log=appium_server_log,
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
    utils_logger.debug("tap_in_point: [" + str(tab_x) + "," + str(tab_y) + "]")
    driver.tap([(tab_x, tab_y)], 2)


def get_screen_shots(driver, file_directory, target_device=None, file_name=None, retry_count=0):
    """
    获取当前截图
    :param file_name: 屏幕截图文件名称
    :param file_directory: 输出目录
    :param driver:
    :param target_device:
    :param retry_count: 
    :return: 
    """
    if driver is None:
        utils_logger.log("failed with no driver")
        return None
    if file_directory is None:
        utils_logger.log("failed with no file_path")
        return None
    utils_logger.debug("[get_screen_shots] screen shot with retry count:" + str(retry_count))
    if file_name is None:
        utils_logger.debug("[get_screen_shots] 构建默认截图存储路径")
        resolution_within_devices = utils_android.get_resolution_by_device(device=target_device)
        file_name = "screen_shot_%s_%s.png" % (
            threading.currentThread().ident,
            resolution_within_devices if resolution_within_devices is not None else "none")
    file_path = os.path.abspath(file_directory + file_name)
    # 删除缓存
    if os.path.exists(file_path):
        utils_logger.debug("get_screen_shots clear cache for file: ", file_path)
        os.remove(file_path)
    try:
        driver.get_screenshot_as_file(file_path)
        return file_path
    except Exception as exception:
        except_name = exception.__class__.__name__  # exception的名称
        utils_logger.log("get_screen_shots caught exception[" + str(except_name) + "]:", retry_count)
        if retry_count > 0 and except_name != "InvalidSessionIdException" and except_name != 'WebDriverException':
            return get_screen_shots(driver=driver, file_directory=file_directory, target_device=target_device,
                                    file_name=file_name, retry_count=retry_count - 1)
        else:
            utils_logger.log("get_screen_shots", traceback.format_exc())
            return None


def get_pg_source(driver, retry_count=0):
    if driver is None:
        utils_logger.log('failed because driver is null')
        return None
    utils_logger.debug("get_pg_source with retry_count:", retry_count)
    try:
        return driver.page_source
    except Exception:
        if retry_count <= 0:
            return None
        else:
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


def find_element_by_content_desc(driver, content_desc, retry_count=0, interval_time=0):
    '查询content-desc字段'
    element = None
    try:
        element = driver.find_element_by_accessibility_id(content_desc)
    finally:
        if element is not None:
            utils_logger.debug(content_desc, "retry_count:" + str(retry_count))
            return element
        elif retry_count <= 0:
            utils_logger.debug(" failed with no chance", content_desc)
            return None
        else:
            if interval_time > 0:
                utils_logger.log("find_element_by_content_desc sleep: " + interval_time)
                time.sleep(interval_time)
            return find_element_by_content_desc(driver, content_desc, retry_count - 1,
                                                interval_time)


def find_element_by_viewid(driver, viewid, retry_count=0, interval_time=0):
    """根据id寻找资源"""
    element = None
    try:
        element = driver.find_element_by_id(viewid)
    finally:
        if element is not None:
            utils_logger.debug(viewid, "retry_count:" + str(retry_count))
            return element
        elif retry_count <= 0:
            utils_logger.debug("failed with no chance", viewid)
            return None
        else:
            if interval_time > 0:
                utils_logger.log("find_element_by_viewid sleep:", interval_time)
                time.sleep(interval_time)
            return find_element_by_viewid(driver=driver, viewid=viewid, retry_count=retry_count - 1,
                                          interval_time=interval_time)


def find_element_by_xpath(driver, xpath, retry_count=0, interval_time=0):
    """基于xpath寻找控件"""
    element = None
    try:
        element = driver.find_element_by_xpath(xpath)
    finally:
        if element is not None:
            utils_logger.debug(xpath, "retry_count:" + str(retry_count))
            return element
        elif retry_count <= 0:
            utils_logger.debug("failed with no chance", xpath)
            return None
        else:
            if interval_time > 0:
                utils_logger.log("find_element_by_xpath sleep: " + interval_time)
                time.sleep(interval_time)
            return find_element_by_xpath(driver=driver, xpath=xpath, retry_count=retry_count - 1,
                                         interval_time=interval_time)


def wait_activity_with_status(driver, target):
    def is_in_fliter(lists, search_fliter):
        if search_fliter is None or lists is None:
            return False

        search_status = False
        for item in lists:
            if item.endswith(search_fliter) is True:
                search_status = True
                break
        return search_status

    """
    等待activity响应
    :param driver: 
    :param target: 待匹配的界面，支持单个字串以及数组
    :return:
    """
    # 格式化搜索条件
    if not isinstance(target, list):
        fliters = [target]
    else:
        fliters = target
    show_activity = get_cur_act(driver=driver)
    if is_in_fliter(fliters, show_activity) is False:
        utils_logger.debug("当前Activity[%s]不在%s目标集合内" % (show_activity, str(fliters)))
        return False
    else:
        return True


def get_driver_by_launch_app(application_id, launch_activity, device_name_to_connected,
                             is_need_setting_input_manager,
                             appium_port, access_appium_bp_port,
                             appium_server_log, retry_count=5):
    """
    启动待测试apk并返回driver对象
    @param application_id:应用名称
    @param access_appium_bp_port:
    @param appium_port: appium服务端口
    @param launch_activity:
    @param device_name_to_connected:
    @param is_need_setting_input_manager: 是否需要添加appium输入法支持
    @param appium_server_log: appium服务的日志输出路径
    @param retry_count:重试次数
    :return: 
    """
    if application_id is None:
        return None
    if launch_activity is None:
        utils_logger.log("请先绑定LAUNCHER页面")
        return None

    # 判断appium服务是否启动
    if start_appium_service(device_name_to_connected, appium_port, access_appium_bp_port, appium_server_log) is False:
        utils_logger.log("appium服务启动失败[端口信息]：" + str(appium_port))
        return None

    platform_version = utils_android.get_deivce_android_version(device=device_name_to_connected)
    # 参数文档查阅:http://appium.io/docs/en/writing-running-appium/caps/
    desired_caps = {'platformName': 'Android',
                    'platformVersion': platform_version,
                    'deviceName': device_name_to_connected,
                    'uuid': utils_android.get_device_tag(device_name_to_connected),
                    'noReset': True,
                    'appPackage': application_id,
                    'appActivity': launch_activity,
                    # 'newCommandTimeout': 3 * 60,  # 无响应再关闭
                    'adbExecTimeout': 50000,
                    'uiautomator2ServerLaunchTimeout': 50000,  # 默认20000
                    'disableWindowAnimation': True,
                    # 'automationName':'uiautomator2'   # todo:还不稳定，观望中
                    }
    if is_need_setting_input_manager is True:
        # 下面两项用于使键盘支持中文输入
        desired_caps['unicodeKeyboard'] = True
        desired_caps['resetKeyboard'] = True
    utils_logger.log("Appium配置参数:", desired_caps, "端口:" + str(appium_port))

    # for循环是用来解决ps查看appium服务存在但实际上appium还未完全启动的情况,此时添加延时重试机制
    for retry_index in range(retry_count):
        try:
            driver = appium_webdriver.Remote("http://127.0.0.1:" + str(appium_port) + '/wd/hub', desired_caps)
            if driver is not None:
                return driver
        except Exception as exception:
            implicat = 20  # 根据日志发现一般在30秒至40秒之内响应
            utils_logger.log("appium服务还未启动[" + str(retry_index) + "],继续等待" + str(implicat) + "秒,异常信息:"
                             + str(exception.__class__.__name__))
            time.sleep(implicat)
    return None


def check_port_avaiable(host, port):
    lsof_out = utils_common.exec_shell_cmd('lsof -i:' + str(port))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.shutdown(2)
    except OSError as e:
        utils_logger.debug('[%s]端口没有被其他服务占用，可以使用' % port)
        return True
    else:
        utils_logger.debug('[%s]端口被其他服务占用了' % port)
        utils_logger.debug("端口占用信息", lsof_out)
        return False


# 查询可用的port值
def query_avaiable_appium_port(start_port, end_port):
    if start_port is None or end_port is None:
        return None
    if start_port > end_port:
        return None
    available_port = start_port
    while available_port <= end_port:
        if check_port_avaiable(host="127.0.0.1", port=available_port) is True:
            return available_port
        else:
            available_port = available_port + 1
    return None


def back_to_target(driver, target_device, application_id=None, target_activity=None, retry_count=5):
    # 回退至指定页
    try_count = 0
    while get_cur_act(driver) != target_activity:
        if try_count > retry_count:
            break
        try:
            driver.keyevent(4)
        except Exception:
            utils_logger.log("返回键事件响应异常")
        finally:
            try_count = try_count + 1
    utils_logger.log("返回键返回至首页,实际重试次数:" + str(try_count))
    if target_activity is not None and get_cur_act(driver) == target_activity:
        return True
    else:
        if application_id is not None and utils_android.get_resume_application_id(target_device) == application_id:
            return True
        else:
            return False


if __name__ == '__main__':
    utils_logger.log(query_avaiable_appium_port(4723, 99999))
