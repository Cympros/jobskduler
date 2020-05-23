#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 用于定义文件操作类
import os
import sys
import time

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../')
sys.path.insert(0, project_root_path)

from helper import utils_logger
from helper import utils_common

def generate_suffix_file(raw_file_path, save_to_dir=None, suffix=None):
    """
    基于源文件构建新的后缀文件
    :param raw_file_path: 
    :param save_to_dir:文件名添加后缀后保存的文件夹名称
    :param suffix: 
    :return: 
    """
    if os.path.exists(raw_file_path) is False:
        utils_logger.log("源文件不能存，不支持创建新的后缀文件", raw_file_path)
        # raise Exception("not support generate_suffix_file with not exist")
        return None
    if os.path.isfile(raw_file_path) is False:
        # raise Exception("not support generate_suffix_file with check file type")
        return None
    if suffix is None:
        # 后缀为空时，以当前时间为后缀
        suffix = utils_common.get_shanghai_time('%Y%m%d%H%M%S')
    format_file_path = os.path.abspath(raw_file_path)  # 规范化文件路径
    if save_to_dir is None:
        dir_name = os.path.dirname(format_file_path)  # 从raw_file_path中截取目录名称
    else:
        if os.path.exists(save_to_dir) is False:
            raise Exception("--->[generate_suffix_file] you should check floder exists:" + save_to_dir)
        dir_name = save_to_dir
    file_name = os.path.basename(format_file_path)  # 包含后缀的文佳名
    single_name, ext = os.path.splitext(file_name)
    return os.path.join(dir_name, single_name + "_" + suffix + ext)


def get_file_modify_time(file_path, time_type='%Y-%m-%d %H:%M:%S'):
    """文件上次更新时间"""
    if os.path.exists(file_path) is False:
        raise Exception('file path not exist')
    return time.strftime(time_type, time.localtime(os.stat(file_path).st_mtime))


def get_file_name_by_file_path(file_path):
    if file_path is None or os.path.exists(file_path) is False:
        return None
    return os.path.basename(file_path)


def write_file(file_path, message):
    """写入文件"""
    with open(file_path, "w") as text_file:
        text_file.write(message)


if __name__ == "__main__":
    get_file_modify_time('image.py')
