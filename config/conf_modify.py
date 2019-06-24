# coding=utf-8
import os
import sys

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)

from helper import utils_config_parser, utils_logger

# job描述相关
# 配置文件格式变更时，务必记得更新下述job_conf_path，已使得配置项重新载入
job_conf_path = os.path.abspath(root_path + "/config/job.config")


def query_jobs():
    '从job列表中读取所有job任务'
    utils_logger.log("---> query_jobs")
    return utils_config_parser.get_sessions(job_conf_path)


def query(job_tag, key, default_value=None):
    '查询对应job下的状态描述信息'
    return utils_config_parser.get_value(job_conf_path, job_tag, key, default_value)


def put(job_tag, key, value):
    '修改对应job下的状态描述'
    if job_tag is None:
        utils_logger.log("---> config_parser不允许填充空session")
        return
    utils_config_parser.put_value(job_conf_path, job_tag, key, value)
