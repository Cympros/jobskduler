# coding=utf-8

# 设备相关工具类
import sys
import os
import re
from PIL import Image

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../')
sys.path.insert(0, project_root_path)

from helper import utils_image as image_utils
from helper import utils_common
from helper import utils_logger


def lock_off_screen_if_need(device):
    if device is None:
        return False
    '解锁当前屏幕'
    cmd_check_screen_off = "adb -s " + device + " shell dumpsys window policy | grep \'mShowingLockscreen=true\'"
    lock_status, lock_status_error = _check_adb_command_result(cmd_check_screen_off)
    if lock_status_error is not None:
        utils_logger.log("lock_off_screen_if_need caught exception:", lock_status_error)
    if lock_status is not None:
        # 锁屏状态
        touch_home, touch_home_error = _check_adb_command_result(
            "adb -s " + device + " shell input keyevent 26 & echo success")
        if touch_home is None:
            utils_logger.log("按home键遭遇异常")
            return False
        swipe_state, swipe_state_error = _check_adb_command_result(
            "adb -s " + device + " shell input swipe 500 50 500 700 & echo success")
        if swipe_state is None:
            utils_logger.log("滑动屏幕解锁失败")
            return False
        # 再次检测屏幕状态
        lock_status, lock_status_error = _check_adb_command_result(cmd_check_screen_off)
        if lock_status_error is not None:
            utils_logger.log("lock_off_screen_if_need retry caught exception:", lock_status_error)
        if lock_status is not None:
            utils_logger.log("尝试解锁失败")
            return False
    return True


def get_resolution_by_device(device):
    '''
        Desc:获取手机的分辨率
        这里涉及到原始分辨率以及当前正在使用的分辨率的区别 
    :param device: 
    :return: 
    '''
    if device is None:
        return None
    # cmd="adb shell wm size" 该方法也可以
    parame = str("" if device is None else "-s " + str(device))
    # 废弃：该命令不支持一加手机 for result:[init=1080x1920 420dpi base=1080x1920 380dpi cur=1080x1920 app=1080x1920 rng=1080x1023-1920x1863]
    # cmd = "adb " + parame + " shell dumpsys window displays | grep cur= | awk '{print $3}'"
    cmd = "adb " + parame + " shell wm size | awk '{print $3}'"
    display, display_error = _check_adb_command_result(cmd)
    if display is not None:
        # 正则校验:最多四位数字 --> \d4 
        if re.match(r'^\d{1,4}x\d{1,4}$', display) is not None:
            return display
        else:
            utils_logger.log("get_resolution_by_devicev failed")
        # if display is not None and display.lstrip().rstrip() != "":
        #     return display.replace("cur=", "").lstrip().rstrip()
        # else:
        return None


def kill_process_by_pkg_name(pkg_name, device):
    '通过包名杀掉进程'
    if pkg_name is None or device is None:
        return
    utils_logger.log("kill_process_by_pkg_name")
    cmd = "adb shell am force-stop '" + pkg_name + "'"
    _check_adb_command_result(cmd)


def get_device_tag(device):
    """获取android设备的唯一标识"""
    # 在第一次启用设备的时候随机生成，并且在用户使用设备时不会发生改变
    if device is None:
        return None
    cmd = "adb" \
          + (" " if device is None else " -s " + str(device) + " ") \
          + "shell settings get secure android_id"
    response, response_error = _check_adb_command_result(cmd)
    return response


def get_deivce_android_version(device):
    if device is None:
        return None
    utils_logger.log("get_deivce_android_version within default:", device)
    cmd = "adb" + (" " if device is None else " -s " + str(device) + " ") \
          + "shell getprop ro.build.version.release"
    # cmd = "adb -s " \
    #       + device_name \
    #       + " shell cat /system/build.prop | grep ro.build.version.release | awk -F '=' '{print $2}' "
    response, response_error = _check_adb_command_result(cmd)
    return None if response is None else response.replace("\n", "")  # 删除换行符


def get_package_path_in_phone_within_applicationid(application_id):
    """通过包名解析出系统目录的apk文件路径"""
    if application_id is None:
        return None
    utils_logger.log("get_package_path_within_applicationid:", application_id)
    cmd = "adb shell pm list packages -f | grep \"" + application_id + "\" | awk -F 'package:|=' '{print $2}'"
    response, response_error = _check_adb_command_result(cmd)
    return response


def get_app_version_by_applicaionid(device, application_id):
    if device is None or application_id is None:
        return None
    cmd = "adb " \
          + (" " if device is None else " -s " + str(device) + " ") \
          + " shell dumpsys package " + str(application_id) \
          + " | grep versionName | awk -F '=' '{print $2}'"
    response, response_error = _check_adb_command_result(cmd)
    return None if response is None else response


def get_battery_status_by_device(device):
    """读取电源状态
    2:充电状态
    """
    if device is None:
        return None
    cmd = "adb " \
          + (" " if device is None else " -s " + str(device) + " ") \
          + " shell dumpsys battery | grep 'AC powered:' | awk -F \":\" '{print $2}'"
    response, response_error = _check_adb_command_result(cmd)
    battery_status = (None if response is None else response)
    if battery_status is None or battery_status != "true":
        utils_logger.log("设备不在线：[", device, "][", response, "][", response_error, "]")
    return battery_status


def get_brand_by_device(device):
    """设备型号"""
    if device is None:
        return None
    cmd = "adb " \
          + (" " if device is None else " -s " + str(device) + " ") \
          + " shell getprop | grep "
    response, response_error = _check_adb_command_result(
        cmd + "ro.product.brand" + " | awk -F ':' '{print $2}'")
    if response is not None:
        return response

    response_vender, response_vender_error = _check_adb_command_result(
        cmd + "ro.product.vendor.brand" + " | awk -F ':' '{print $2}'")
    return response_vender


def get_model_by_device(device):
    """设备版本"""
    if device is None:
        return None
    cmd = "adb " \
          + (" " if device is None else " -s " + str(device) + " ") \
          + " shell getprop | grep "
    response, response_error = _check_adb_command_result(
        cmd + "ro.product.model" + " | awk -F ':'  '{print $2}'")
    if response is not None:
        return response

    response_vender, response_vender_error = _check_adb_command_result(
        cmd + "ro.product.vendor.model" + " | awk -F ':'  '{print $2}'")
    return response_vender


def pull_file_from_phone(file_path_in_phone, target_dir_in_mac):
    """copy 手机中的文件至电脑当中(todo:需要root权限)
    @:param file_path_in_phone
    @:param target_dir_in_mac 
    """
    cmd = "adb pull " + file_path_in_phone + " " + target_dir_in_mac
    response = _check_adb_command_result(cmd)
    if response is not None:
        return target_dir_in_mac
    return None


def get_top_focuse_activity(device):
    """获取当前打开应用的信息"""
    if device is None:
        return None
    cmd = "adb " \
          + (" " if device is None else " -s " + str(device) + " ") \
          + " shell dumpsys activity | grep -E 'mFocusedActivity|ResumedActivity'"
    response, response_errror = _check_adb_command_result(cmd)
    return response


def get_package_name_by_apk(apk_path):
    '解析apk获取包名'
    utils_logger.log("get_package_name_by_apk")
    cmd = "aapt dump badging " + apk_path \
          + " | awk '{printf $0\"\\\n\"}' | head -1 | awk -F 'name=' '{print $2}' | awk '{print $1}'"
    response, response_errror = _check_adb_command_result(cmd)
    return None if response is None else response.replace("'", "").replace("\n", "")


def get_connected_devcies(target_device=None, except_emulater=False):
    '''
        说明：获得已经连接成功的设备，若target_device设备不存在，则返回所有可用设备
        参数：except_emulater是否排除模拟器
            
    '''
    device_infos, device_infos_errror = _check_adb_command_result("adb devices")
    if device_infos is None:
        utils_logger.log("> get_connected_devcies:device_infos is None")
        return None
    contected_devices = []
    for device_info in device_infos.split("\n"):
        trim_device_info = device_info.lstrip().rstrip()
        if trim_device_info != "" and trim_device_info != "List of devices attached":
            # utils_logger.log("get_connected_devcies 解析的android设备:" + device_info)
            split_array = trim_device_info.split('\t')
            # utils_logger.log("[split_array]:",split_array)
            trim_device_info = split_array[0]
            if split_array[1] != "device":
                # utils_logger.log("[设备状态" + split_array[1] + "]:", trim_device_info)
                utils_common.exec_shell_cmd("adb -s " + trim_device_info + " disconnect")
                continue
            if except_emulater and trim_device_info.startswith('emulator-'):
                continue
            else:
                if target_device is not None and trim_device_info == target_device:
                    del contected_devices[:]  # 清空数组
                    contected_devices.append(trim_device_info)
                    break
                else:
                    contected_devices.append(trim_device_info)
    return contected_devices


def get_start_activity_by_application_id(application_id):
    '通过apk解析启动页'
    if application_id is None:
        return None
    # todo:'adb shell dumpsys activity'需要应用在后台是存活的
    cmd = "adb shell dumpsys activity | grep 'android.intent.category.LAUNCHER' " \
          + " | awk '{for(i=1;i<=NF;i++){if($i~/cmp/){print $i}}}' | awk -F 'cmp=' '{print $2}'" \
          + " | grep -v 'bnds='" \
          + " | grep '" + application_id + "'"
    response, response_errror = _check_adb_command_result(cmd)
    # 拼接launcher_activity
    launcher_activity = None
    if response is not None:
        split_activity = response.split("/")[1]
        utils_logger.log("[split_activity]", split_activity)
        if split_activity.startswith(".") is True:
            launcher_activity = application_id + split_activity
        else:
            launcher_activity = split_activity
    utils_logger.log("[get_start_activity_by_application_id]", launcher_activity)
    return launcher_activity


def get_device_statue(device):
    """读取设备在线状态"""
    if device is None:
        return None
    device_infos, device_infos_errror = _check_adb_command_result("adb devices")
    if device_infos is None:
        return None
    for device_info in device_infos.split("\n"):
        trim_device_info = device_info.lstrip().rstrip()
        if trim_device_info != "" and trim_device_info != "List of devices attached":
            split_array = trim_device_info.split('\t')
            trim_device_info = split_array[0]
            if trim_device_info == device:
                return split_array[1]
    return None


def is_app_installed(device, application_id):
    if device is None or application_id is None:
        return None, None
    # "-3"参数表示仅过滤第三方应用
    cmd = "adb " \
          + (" " if device is None else " -s " + device + " ") \
          + " shell pm list packages -3 | grep " + str(application_id)
    check_installed_response, response_errror = _check_adb_command_result(cmd)
    utils_logger.log(check_installed_response, response_errror)
    return check_installed_response, response_errror


def _check_adb_command_result(adb_cmd, retry_count=3):
    # 用于针对adb命令的异常处理
    res_adb, error_adb = utils_common.exec_shell_cmd(adb_cmd)
    if retry_count <= 0:
        utils_logger.log("cmd[" + str(adb_cmd) + "],"
                         + "retry_count[" + str(retry_count) + "]")
        utils_logger.log("response:[" + str(res_adb) + "],"
                         + "error:[" + str(error_adb) + "]")
        return res_adb, error_adb
    if error_adb is not None:  # 表示有异常
        if "error: device " in error_adb.decode() and " not found" in error_adb.decode():
            # 重启adb服务
            # utils_common.exec_shell_cmd("adb kill-server && adb start-server")
            return _check_adb_command_result(adb_cmd, retry_count - 1)
    utils_logger.log("cmd[" + str(adb_cmd) + "],"
                     + "retry_count[" + str(retry_count) + "]")
    utils_logger.log("response:[" + str(res_adb) + "],"
                     + "error:[" + str(error_adb) + "]")
    return res_adb, error_adb


def is_page_loging(check_file, x_cut_count=5, y_cut_count=10):
    '''
    判断图片是否有大片留白,方案：先大图裁剪成不同部分的小图，然后针对每张小图校验是否其为纯色图片
    # 注释：x_cut_count与y_cut_count最好不要自定义，太细会使得每张小图都是纯色图片，但纯色图的色值不同
    @:param x_cut_count  横向拆分数
    @:param y_cut_count 纵向拆分数
    :return: 
    '''
    image_resorce = Image.open(check_file)
    # 这里务必根据图片自身宽高来进行切片，不要会用分辨率的宽高
    utils_logger.log("---image_resorce:", image_resorce.size)
    item_width = int(image_resorce.size[0]) / x_cut_count  # 切片的横向宽度
    item_height = int(image_resorce.size[1]) / y_cut_count  # 切片的宽度
    solid_dict = {}  # 纯色出片存储
    for x_cut_index in range(x_cut_count):
        for y_cut_index in range(y_cut_count):
            # utils_logger.log("is_page_loging:",x_cut_index,y_cut_index
            # crop参数以(left, top, right, bottom)方式组织
            rect_formted = (
                x_cut_index * item_width, y_cut_index * item_height, (1 + x_cut_index) * item_width,
                (1 + y_cut_index) * item_height)
            # utils_logger.log("---rect_formted:",rect_formted
            is_solid, rgba = image_utils.get_color_if_img_solid(image_resorce.crop(rect_formted))
            if is_solid is False:
                continue
            # utils_logger.log("rgb:",rgba
            rgb_key = "".join(str(rgba))
            if solid_dict.has_key(rgb_key):
                solid_dict[rgb_key] = int(solid_dict[rgb_key]) + 1
            else:
                solid_dict[rgb_key] = 0
    utils_logger.log("各纯色块及数量:", solid_dict)
    if len(solid_dict) == 0:
        utils_logger.log("不存在纯色子图，因此认为页面已绘制完成")
        return False
    else:
        max_solid_count = max(solid_dict.values())  # 纯色区域中占用最大色块的色块数
        is_solid = (5 * max_solid_count > 3 * (x_cut_count * y_cut_count))
        utils_logger.log("max_solid_count:", max_solid_count,
                         ",max_solid_count/total_size>约定阈值:", is_solid)
        # 最大的纯色区域占据2/3以上的部分则表示页面还在加载中
        if is_solid:
            utils_logger.log("纯色区域比例大于阈值，认为页面还未加载完成")
            return True
        else:
            utils_logger.log("纯色区域比例小于阈值，因此认为页面已绘制完成")
            return False
