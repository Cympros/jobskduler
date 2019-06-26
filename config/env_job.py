# coding=utf-8

import os


def get_module_root_path():
    module_root_dir = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + "/../")
    return module_root_dir


def get_yaml_path():
    return get_out_dir() + "/schduler.yaml"


def get_out_dir():
    '临时文件的存放跟目录'
    outer_dir = get_module_root_path() + "/out/"
    if not os.path.exists(outer_dir):
        os.makedirs(outer_dir)
    return outer_dir


def get_log_file():
    """返回日志文件存储路径"""
    return get_out_dir() + 'logger.log.txt'


def get_append_log_file():
    """返回日志文件存储路径"""
    return get_out_dir() + 'append_logger.log.txt'


def get_appium_img_dir():
    'appium下存放img的目录'
    appium_img_dir = os.path.abspath(get_module_root_path() + "/job/appium/img")
    if not os.path.exists(appium_img_dir):
        return None
    return appium_img_dir


if __name__ == "__main__":
    get_out_dir()
