# coding=utf-8

import os
import sys
import zipfile

root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../')
sys.path.append(root_path)

from helper import utils_common, utils_file, utils_logger


def get_module_root_path():
    module_root_dir = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + "/../")
    return module_root_dir


def get_db_path():
    return os.path.abspath(get_out_dir() + "/schduler.db")


def get_job_config_path():
    return os.path.abspath(root_path + "/data/job.config")


def get_yaml_path():
    return get_out_dir() + "/schduler.yaml"


def get_out_dir():
    '临时文件的存放跟目录'
    outer_dir = get_module_root_path() + "/out/"
    if not os.path.exists(outer_dir):
        os.makedirs(outer_dir)
    return outer_dir


def zip_msg_within_files(file_name, message, files=None):
    log_zip_dir = get_out_dir() + "/log_zip/"
    if os.path.exists(log_zip_dir) is False:
        os.mkdir(log_zip_dir)
    new_zip = zipfile.ZipFile(log_zip_dir + ("" if file_name is None else file_name)
                              + utils_common.get_shanghai_time("%Y%m%d%H%M%S") + ".zip", 'w')
    if message is not None:
        message_path = os.path.abspath(get_out_dir() + "/message.txt")
        utils_file.write_file(message_path, message)
        new_zip.write(message_path, utils_file.get_file_name_by_file_path(message_path), zipfile.ZIP_DEFLATED)
    if files is not None:
        for file_path_item in files:
            if os.path.exists(file_path_item) is False:
                continue
            new_zip.write(file_path_item, utils_file.get_file_name_by_file_path(file_path_item), zipfile.ZIP_DEFLATED)


def get_appium_img_dir():
    'appium下存放img的目录'
    appium_img_dir = os.path.abspath(get_module_root_path() + "/job/appium/img")
    if not os.path.exists(appium_img_dir):
        return None
    return appium_img_dir


if __name__ == "__main__":
    zip_msg_within_files("&&&&", [utils_logger.get_log_file()])
