# coding=utf-8
import os
import sys

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(project_root_path)

import shlex
import subprocess
import re
import json
import imagehash
import time
import datetime
import hashlib

try:
    import pytz
except:
    os.system('sudo pip install pytz')
    import pytz
import socket
import traceback
import colorsys
from PIL import Image

from helper import utils_logger


def get_shanghai_time(str_mode=None):
    """获取上海时间，str_mode标识时间格式"""
    if str_mode is None:
        return int(time.time())
    tz = pytz.timezone('Asia/Shanghai')
    fromtimestamp = datetime.datetime.fromtimestamp(int(time.time()), tz)
    utils_logger.log("格式化样式[" + str_mode + "]:", fromtimestamp.strftime(str_mode))
    return fromtimestamp.strftime(str_mode)


def is_img_similary(file_first, file_second, hash_rule=100):
    """ 功能说明： hash_rule:# 小于100表示相似，否则不相似，尽量处理的严格一点
    :param file_first: 
    :param file_second: 
    :param hash_rule: 
    :return: compare_status--> boolean
    """
    highfreq_factor = 1
    hash_size = 20
    img_size = hash_size * highfreq_factor

    hash_first = imagehash.phash(Image.open(file_first), hash_size=hash_size,
                                 highfreq_factor=highfreq_factor)
    hash_second = imagehash.phash(Image.open(file_second), hash_size=hash_size,
                                  highfreq_factor=highfreq_factor)
    utils_logger.log(file_first, ": ", hash_first)
    utils_logger.log(file_second, ": ", hash_second)
    compare_status = True if hash_first - hash_second <= hash_rule else False
    if compare_status is False:
        utils_logger.log("is_similary:" + str(compare_status), \
                         ",other_info:[", hash_second - hash_first, \
                         len(hash_second.hash), "]")
    return compare_status


def exec_shell_cmd(cmd_str, timeout=None, shell=True):
    """功能说明：执行SHELL命令
        封装subprocess的Popen方法, 支持超时判断，支持读取stdout和stderr
        参数:
            cwd: 运行命令时更改路径，如果被设定，子进程会直接先更改当前路径到cwd
            timeout: 超时时间，秒，支持小数，精度0.1秒
            shell: 是否通过shell运行
        Returns: (response_stdout，response_error)
    """
    if shell:
        cmdstr_list = cmd_str
    else:
        cmdstr_list = shlex.split(cmd_str)
    if timeout is not None:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    # 没有指定标准输出和错误输出的管道，因此会打印到屏幕上；
    utils_logger.log("\"" + cmd_str + "\"")
    sub = subprocess.Popen(cmdstr_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=shell, bufsize=4096)

    while sub.poll() is None:
        sleep_time = 0.1
        time.sleep(sleep_time)
        if timeout is not None and end_time <= datetime.datetime.now():
            return None, None

    response_stdout = sub.stdout.read().lstrip().rstrip()
    if response_stdout is not None and response_stdout != "":
        return response_stdout.decode(), None

    response_error = sub.stderr.read().lstrip().rstrip()
    if response_error is not None and response_error != "":
        utils_logger.log("shell执行异常:", response_error)
        return None, response_error.decode()
    return None, None


def get_file_md5(filename):
    """获取文件的md5标识"""
    if filename is None:
        return None
    if not os.path.isfile(filename):
        return None
    # filemt= time.localtime(os.stat(filename).st_mtime)
    # utils_logger.log("[modify time]： ",time.strftime("%Y%m%d %H:%M:%S",filemt)
    myhash = hashlib.md5()
    f = file(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def get_real_host_ip():
    """
    查询本机ip地址,区别于socket.gethostbyname(socket.gethostname())
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        utils_logger.log(traceback.format_exc())
    finally:
        s.close()
    return ip


def get_host_name():
    """查询主机名称"""
    return socket.gethostname()


def get_file_content(file):
    with open(file, 'rb') as fp:
        return fp.read()


def get_dominant_color(file_image):
    image = Image.open(file_image)
    '输出图片的主要颜色值'
    # 颜色模式转换，以便输出rgb颜色值
    image = image.convert('RGBA')
    # 生成缩略图，减少计算量，减小cpu压力
    # image.thumbnail((200, 200))
    max_score = None
    dominant_color = None

    for count, (r, g, b, a) in image.getcolors(image.size[0] * image.size[1]):
        # 跳过纯黑色
        if a == 0:
            continue
        saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
        y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
        y = (y - 16.0) / (235 - 16)
        # 忽略高亮色
        if y > 0.9:
            continue
            # Calculate the score, preferring highly saturated colors.
        # Add 0.1 to the saturation so we don't completely ignore grayscale
        # colors by multiplying the count by zero, but still give them a low
        # weight.
        score = (saturation + 0.1) * count
        # utils_logger.log( saturation, count, score, max_score
        if score > max_score:
            max_score = score
            dominant_color = (r, g, b)
    utils_logger.log((image.size[0] * image.size[1]))
    # len(image.getcolors(image.size[0] * image.size[1]))
    utils_logger.log("max_score:", max_score)
    return dominant_color


# 指数衰减函数,随着时间的扩大衰减速度越来越慢,真好可以用于定义到下次执行的时间间隔
# t:时间节点
# length:衰减周期长度
# init:初始衰减值
# finish:结束衰减值
def exponential_decay(time, length, init=1, finish=0.15):
    import numpy as np
    alpha = np.log(init / finish) / length
    l = - np.log(init) / alpha
    decay = np.exp(-alpha * (time + l))
    return decay


if __name__ == "__main__":
    # utils_logger.log(get_points_within_text('../test/job_scheduler_out_screen_tmp_600x1024_meirifuli.png', r'京东用户每日福利')
    # utils_logger.log(_get_point_within_text_tencentapi("../test/job_scheduler_out_screen_tmp_600x1024_double_quqiandao.png",'去签到')
    # utils_logger.log(get_points_within_text("../test/screen_shot_jingdou_peiyucang.png","1")

    # utils_logger.log(get_color_if_img_solid(Image.open('../test/job_scheduler_out_screen_tmp_600x1024_double_quqiandao.png'))
    # utils_logger.log(get_color_if_img_solid(Image.open('../test/test_solid.png'))
    # utils_logger.log(get_color_if_img_solid(Image.open('../test/pingmukuiazhao.png'))

    # 正则表达式解析
    # 数字的一般形式：'----.-----',可得"\d+\.?\d*"
    # \d+匹配1次或者多次数字，注意这里不要写成*，因为即便是小数，小数点之前也得有一个数字；\.?这个是匹配小数点的，可能有，也可能没有；\d*这个是匹配小数点之后的数字的，所以是0个或者多个；
    # utils_logger.log("success" if re.match(r'您已签到并领取\d+金币','您已签到并领取150金币') is not None else "None"  # --->success
    # utils_logger.log("success" if re.match(r'签到\+.里程','签到+2里程') is not None else "None"    # --->success
    # utils_logger.log("success" if re.match(r'^签到$','签到') is not None else "None"       # --->success
    # utils_logger.log("success" if re.match(r'^签到$','您还有0次抽奖机会') is not None else "None"      # --->None

    # text_matcher=r'^已签\d天($|(,|，)坐等开奖$)'
    # utils_logger.log("success" if re.match(text_matcher,'已签3天') is not None else "None"  # --->success
    # utils_logger.log("success" if re.match(text_matcher,'已签3天,坐等开奖') is not None else "None" # --->success
    # utils_logger.log("success" if re.match(text_matcher,'已签3天,坐等开奖t') is not None else "None"    # --->None
    # utils_logger.log("success" if re.match(text_matcher,'已签3天，坐等开奖') is not None else "None" # --->success

    # utils_logger.log("success" if re.match(r'签到领3元无门槛*','签到领3元无门槛高') is not None else "None"   # ---> success
    # # 下面两条记录针对打卡在首位以及在末尾
    # utils_logger.log("success" if re.match(r'打卡','早起打卡') is not None else "None" # ---> None
    # utils_logger.log("success" if re.match(r'打卡','打卡倒计时') is not None else "None" # ---> success
    # utils_logger.log("success" if re.match(r'^打卡','打卡倒计时') is not None else "None" # ---> success
    utils_logger.log("success" if re.match(r'^打卡[0-9]+([.]{1}[0-9]+){0,1}时间',
                                           '打卡8.73336655时间') is not None else "None")  # ---> success

    # # 元素切割：for youdao
    # strs=u'95,191,248,192,248,224,95,223'
    # point_tmp_list = list(map(int, re.split(',', strs)))
    # utils_logger.log(point_tmp_list
    # # 获取行位置的下标信息
    # point_left = int(min(point_tmp_list[::2]))  # 偶数项
    # point_top = int(min(point_tmp_list[1::2]))  # 奇数项
    # width = int(max(point_tmp_list[::2])) - point_left
    # height = int(max(point_tmp_list[1::2])) - point_top
    # utils_logger.log(point_left, point_top, width, height

    # utils_logger.log(get_dominant_color('../out/ericp_600x1024.png')
    # get_point_range('../out/A.png', '../out/bb.png')
    utils_logger.log(exec_shell_cmd("adb devices"))
