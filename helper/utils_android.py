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


def close_heads_up_notifycations(device=None):
    """禁用抬头通知"""
    close_cmd = "adb %s shell settings put global heads_up_notifications_enabled 0" % \
                ("" if device is None else "-s " + str(device))
    close_status, close_status_error = _check_adb_command_result(close_cmd)
    if close_status_error is not None:
        return False
    else:
        utils_logger.debug(close_status, close_status_error)
        return True


def lock_off_screen_if_need(device=None):
    """解锁当前屏幕"""
    cmd_check_screen_off = "adb %s shell dumpsys window policy | grep 'mShowingLockscreen=true'" % \
                           ("" if device is None else "-s " + str(device))
    lock_status, lock_status_error = _check_adb_command_result(cmd_check_screen_off)
    if lock_status_error is not None:
        utils_logger.log("lock_off_screen_if_need caught exception:", lock_status_error)
    if lock_status is not None:
        # 锁屏状态
        touch_home, touch_home_error = _check_adb_command_result(
            "adb %s shell input keyevent 26 & echo success" % ("" if device is None else "-s " + str(device)))
        if touch_home is None:
            utils_logger.log("按home键遭遇异常")
            return False
        swipe_state, swipe_state_error = _check_adb_command_result(
            "adb %s shell input swipe 500 50 500 700 & echo success" % ("" if device is None else "-s " + str(device)))
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


def get_resolution_by_device(device=None):
    '''
        Desc:获取手机的分辨率
        这里涉及到原始分辨率以及当前正在使用的分辨率的区别 
    :param device: 
    :return: 
    '''
    # 其他方案:正则
    # clear_btn_loc = re.search(r'Physical size: (\d+)x(\d+)', result)
    # x = int(clear_btn_loc.group(1))
    # y = int(clear_btn_loc.group(2))

    # cmd="adb shell wm size" 该方法也可以
    parame = str("" if device is None else "-s " + str(device))
    # 废弃：该命令不支持一加手机 for result:[init=1080x1920 420dpi base=1080x1920 380dpi cur=1080x1920 app=1080x1920 rng=1080x1023-1920x1863]
    # cmd = "adb " + parame + " shell dumpsys window displays | grep cur= | awk '{print $3}'"
    cmd = "adb %s shell wm size | awk '{print $3}'" % parame
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


def get_device_tag(device=None):
    """获取android设备的唯一标识"""
    # 在第一次启用设备的时候随机生成，并且在用户使用设备时不会发生改变
    cmd = "adb %s shell settings get secure android_id" % ("" if device is None else "-s " + str(device))
    response, response_error = _check_adb_command_result(cmd)
    return response


def get_resume_application_id(device=None):
    """读取当前展示应用的applicationId"""
    cmd = "adb %s shell dumpsys activity activities | grep 'ResumedActivity' | grep \"/\" |head -n 1" % \
          ("" if device is None else "-s " + str(device))
    response, response_error = _check_adb_command_result(cmd)
    if response is None:
        cmd = "adb %s shell dumpsys window | grep 'mCurrentFocus' | grep \"/\" | head -n 1" % \
              ("" if device is None else "-s " + str(device))
        response, response_error = _check_adb_command_result(cmd)
    if response is not None:
        cmd = "echo \"%s\" | awk -F ' |{|}' '{for(i=1;i<=NF;i++){if($i ~ \"'/'\"){print $i;}}}' " \
              "| awk -F '/' '{print $1}'" % response
        response, response_error = _check_adb_command_result(cmd)
        return response
    else:
        return None


def get_resumed_activity(device=None):
    cmd = "echo \"$(adb " + (" " if device is None else " -s " + str(device) + " ") \
          + "shell dumpsys activity activities | grep 'ResumedActivity') \\n $(adb " \
          + (" " if device is None else " -s " + str(device) + " ") \
          + "shell dumpsys window | grep 'mCurrentFocus')\" | head -n 1 | awk -F ' |{|}' '{for(i=1;i<=NF;i++){if($i ~ " \
            "\"'/'\"){print $i;}}}' "
    response, response_error = _check_adb_command_result(cmd)
    utils_logger.debug("exec结果:", response, response_error)
    if response is None:
        return None
    texts = response.split("/")
    if len(texts) != 2:
        return None
    utils_logger.debug("分解结果:", texts[0], texts[1])
    if texts[1].startswith("."):
        return texts[0] + texts[1]
    else:
        return texts[1]


def get_deivce_android_version(device=None):
    cmd = "adb %s shell getprop ro.build.version.release" % \
          ("" if device is None else "-s " + str(device))
    response, response_error = _check_adb_command_result(cmd)
    return None if response is None else response.replace("\n", "")  # 删除换行符


def get_app_version_by_applicaionid(device, application_id):
    if application_id is None:
        return None
    cmd = "adb %s shell dumpsys package %s | grep versionName | awk -F '=' '{print $2}'" % \
          (("" if device is None else "-s " + str(device)), str(application_id))
    response, response_error = _check_adb_command_result(cmd)
    return None if response is None else response


def get_brand_by_device(device=None):
    """设备型号"""
    cmd = "adb %s shell getprop | grep ro.product.brand | awk -F ':' '{print $2}'" % \
          ("" if device is None else "-s " + str(device))
    response, response_error = _check_adb_command_result(cmd)
    if response is not None:
        return response

    response_vender, response_vender_error = _check_adb_command_result(
        cmd + "ro.product.vendor.brand" + " | awk -F ':' '{print $2}'")
    return response_vender


def get_model_by_device(device=None):
    """设备版本"""
    cmd = "adb %s shell getprop | grep 'ro.product.model' | awk -F ':' '{print $2}'" % \
          ("" if device is None else "-s " + str(device))
    response, response_error = _check_adb_command_result(cmd)
    if response is not None:
        return response

    response_vender, response_vender_error = _check_adb_command_result(
        cmd + "ro.product.vendor.model" + " | awk -F ':'  '{print $2}'")
    return response_vender


def get_top_focuse_activity(device=None):
    """获取当前打开应用的信息"""
    cmd = "adb %s shell dumpsys activity | grep -E 'mFocusedActivity|ResumedActivity'" % \
          ("" if device is None else "-s " + str(device))
    response, response_errror = _check_adb_command_result(cmd)
    return response


def get_package_name_by_apk(apk_path):
    """解析apk获取包名"""
    cmd = "aapt dump badging %s | awk '{printf $0\"\\\n\"}' | head -1 | awk -F 'name=' '{print $2}' | awk '{print $1}'" \
          % apk_path
    response, response_errror = _check_adb_command_result(cmd)
    return None if response is None else response.replace("'", "").replace("\n", "")


def get_connected_devcies(target_device=None, except_emulater=False):
    """
    说明：获得已经连接成功的设备，若target_device设备不存在，则返回所有可用设备
    参数：except_emulater是否排除模拟器

"""
    device_infos, device_infos_errror = _check_adb_command_result("adb devices | grep -v 'List of devices attached'")
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


def get_device_statue(device=None):
    """读取设备在线状态"""
    cmd = "adb %s get-state" % ("" if device is None else "-s " + str(device))
    device_status, device_status_errror = _check_adb_command_result(cmd)
    return device_status


def is_app_installed(device, application_id):
    if application_id is None:
        return None, None
    # "-3"参数表示仅过滤第三方应用
    cmd = "adb %s shell pm list packages -3 | grep '%s'" % \
          (("" if device is None else "-s " + device), str(application_id))
    check_installed_response, response_errror = _check_adb_command_result(cmd)
    # utils_logger.log(check_installed_response, response_errror)
    return check_installed_response, response_errror


def _check_adb_command_result(adb_cmd, retry_count=3):
    # 用于针对adb命令的异常处理
    res_adb, error_adb = utils_common.exec_shell_cmd("timeout 5 %s" % adb_cmd)
    if retry_count <= 0:
        return res_adb, error_adb
    if error_adb is not None:  # 表示有异常
        if "adb: protocol fault" in error_adb:
            # 重启adb服务
            utils_common.exec_shell_cmd("adb kill-server && adb start-server")
            return _check_adb_command_result(adb_cmd, retry_count - 1)
    return res_adb, error_adb


def is_page_loging(check_file, x_cut_count=5, y_cut_count=10):
    """
    判断图片是否有大片留白,方案：先大图裁剪成不同部分的小图，然后针对每张小图校验是否其为纯色图片
    # 注释：x_cut_count与y_cut_count最好不要自定义，太细会使得每张小图都是纯色图片，但纯色图的色值不同
    @:param x_cut_count  横向拆分数
    @:param y_cut_count 纵向拆分数
    :return: 
    """
    image_resorce = Image.open(check_file)
    # 这里务必根据图片自身宽高来进行切片，不要会用分辨率的宽高
    utils_logger.debug("---image_resorce:", image_resorce.size)
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
            if rgb_key in solid_dict:
                solid_dict[rgb_key] = int(solid_dict[rgb_key]) + 1
            else:
                solid_dict[rgb_key] = 0
    utils_logger.debug("各纯色块及数量:", solid_dict)
    if len(solid_dict) == 0:
        utils_logger.debug("不存在纯色子图，因此认为页面已绘制完成")
        return False
    else:
        max_solid_count = max(solid_dict.values())  # 纯色区域中占用最大色块的色块数
        is_solid = (5 * max_solid_count > 3 * (x_cut_count * y_cut_count))
        utils_logger.debug("max_solid_count:", max_solid_count,
                           ",max_solid_count/total_size>约定阈值:", is_solid)
        # 最大的纯色区域占据2/3以上的部分则表示页面还在加载中
        if is_solid:
            utils_logger.log("纯色区域比例大于阈值，认为页面还未加载完成")
            return True
        else:
            utils_logger.debug("纯色区域比例小于阈值，因此认为页面已绘制完成")
            return False


def get_battery_level(device=None, default=0):
    # 获取剩余电量
    cmd = "adb %s shell dumpsys battery | grep 'level:'" % ("" if device is None else "-s " + str(device))
    response, error = _check_adb_command_result(cmd)
    if response is not None:
        return int(response.split(':')[1].strip())
    else:
        return default


if __name__ == '__main__':
    # print(get_resumed_activity())
    # print(get_resume_application_id())
    print("[" + str(get_battery_level()) + "]")
