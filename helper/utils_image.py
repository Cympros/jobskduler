#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from PIL import Image

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(project_root_path)

from helper import utils_logger

from helper import utils_file as FileOperate
from helper import envs


def get_rect_formated(raw_file_path, cutted_scale=[0, 1, 0, 1]):
    """
    将纯比例根据图片大小转换为响应的point点标
    :param raw_file_path: 
    :param cutted_scale: 
    :return: 
    """
    image_resorce = Image.open(raw_file_path)
    image_width = int(image_resorce.size[0])  # 图片宽度
    image_height = int(image_resorce.size[1])  # 图片高度
    utils_logger.log("[cutted_image_with_scale] image_width:", image_width, ",image_height:", image_height,
                     ",cutted_rect:", cutted_scale)
    # crop参数以(left, top, right, bottom)方式组织，因此需要从cutted_rect转换
    rect_formted = (int(float(image_width) * cutted_scale[0]), int(float(image_height) * cutted_scale[2]),
                    int(float(image_width) * cutted_scale[1]), int(float(image_height) * cutted_scale[3]))
    return rect_formted


def cutted_image_with_scale(raw_file_path, cutted_save_file_path=None, cutted_rect_scale=[0, 1, 0, 1]):
    """
    Desc:以纯比例方式裁剪图片
    cutted_rect:以[横向左边界，横向右边界，垂直上边界，垂直下边界]
    """
    rect_formted = get_rect_formated(raw_file_path=raw_file_path, cutted_scale=cutted_rect_scale)
    return cutted_image(raw_file_path=raw_file_path, cutted_save_file_path=cutted_save_file_path,
                        rect_formted=rect_formted)


def cutted_image(raw_file_path, cutted_save_file_path=None, rect_formted=None):
    """
    Desc:按坐标对raw_file_path路径图片进行裁剪
    cutted_save_file_path:裁剪后的图片保存路径,默认保存在源目录，添加_cutted后缀
    """
    if rect_formted is None:
        raise Exception("请先设置裁剪区域")
    if cutted_save_file_path is None:
        cutted_save_file_path = FileOperate.generate_suffix_file(raw_file_path=raw_file_path, suffix='cutted')
    utils_logger.log("[cutted_image] rect_formted(left,top,right,bottom):", rect_formted)
    Image.open(raw_file_path) \
        .crop((rect_formted)) \
        .save(cutted_save_file_path)
    if not os.path.exists(cutted_save_file_path):
        utils_logger.log("截图失败")
        return None
    utils_logger.log("[cutted_image] cutted_image.截图保存路径：", os.path.abspath(cutted_save_file_path))
    return cutted_save_file_path


def get_color_if_img_solid(raw_image):
    """
    desc:若是纯色图片，则返回True以及色值
    定义：第一颜色值与第二颜色值相差1000倍数，即可定义为纯色图片
    :param image: 是使用Image.open或者crop处理过的元素集 
    :return: 
    """
    # utils_logger.log("---------------> start check get_color_if_img_solid"
    # 颜色模式转换，以便输出rgb颜色值
    image = raw_image.convert('RGBA')
    image_colors = image.getcolors(image.size[0] * image.size[1])
    if len(image_colors) == 1:
        utils_logger.log("是纯色图片:颜色唯一")
        return True, image_colors[0][1]
    else:
        max_color_count = 0
        max_rgba = None
        for count, (r, g, b, a) in image_colors:
            if count > max_color_count:
                max_color_count = count
                max_rgba = (r, g, b, a)
        if 1000 * max_color_count / (image.size[0] * image.size[1]) > 999:
            utils_logger.log("第一梯队颜色值比例超过99.9%，可认为是纯色图片")
            return True, max_rgba
    # utils_logger.log("not 纯色图片"
    return False, None


if __name__ == '__main__':
    file = root_path + 'tasks/appium/img/jingdong_double_sign_enterence.png'
    cutted_file_path = FileOperate.generate_suffix_file(file, save_to_dir=envs.get_out_dir(), suffix="cutted")
    cutted_image_with_scale(raw_file_path=file, cutted_save_file_path=cutted_file_path,
                            cutted_rect_scale=[0.82, 0.98, 0.47, 0.568])
