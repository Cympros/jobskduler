# coding=utf-8
import os
import sys

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)
from config import utils_logger

'''
针对配置文件的读取修改工具类
'''
import ConfigParser

dict_cf = {}  # 定义字典，用于存储配置文件与cf对象的映射关系


def __generate_config_parser(conf_path):
    '根据conf_path返回可用的ConfigParser对象'
    if dict_cf.has_key(conf_path) is False or dict_cf[conf_path] is None:
        # "重新构造配置文件对应的ConfigParser对象"
        utils_logger.log("__generate_config_parser", conf_path)
        # 指配置文件对应的ConfigParser对象还没有被创建
        cf = ConfigParser.ConfigParser()
        cf.read(conf_path)
        dict_cf[conf_path] = cf
    else:
        cf = dict_cf[conf_path]
    return cf


def get_value(conf_path, session, key, default_value=None):
    '''
    从指定conf_path中取值
    :param session:
    :param key:
    :param default_value:
    :param conf_path: 配置文件地址
    :return:
    '''
    # utils_logger.log("-----> [utils_conf.get_value] conf_path:",conf_path
    # utils_logger.log( "---> [utils_conf.get_value]续：" ,"session:", session, ",key:", key, ",default_value:", default_value
    cf = __generate_config_parser(conf_path=conf_path)
    # utils_logger.log("---> query:", job_tag, ",", key, ",", default_value, ",", force_reload
    if cf is not None and cf.has_section(session) and cf.has_option(session, key):
        return cf.get(session, key)
    else:
        if not cf:
            utils_logger.log("cf not init: ", session, key)
        elif not cf.has_section(session):
            utils_logger.log("no selection: ", session, key)
        elif not cf.has_option(session, key):
            utils_logger.log("no option: ", session, key)
        # 配置项反写操作(仅支持cf非空且session非空的情况)
        if cf is not None and cf.has_section(session) and default_value is not None:
            put_value(conf_path=conf_path, session=session, key=key, value=default_value)
        return default_value


def put_value(conf_path, session, key, value):
    '''
    写入指定配置文件
    :param conf_path:
    :param session:
    :param key:
    :param value:
    :return:
    '''
    # utils_logger.log("-----> [utils_conf.put_value] conf_path:",conf_path
    # utils_logger.log( "---> [utils_conf.put_value]续：" ,"session:", session, ",key:", key, ",value:", value
    cf = __generate_config_parser(conf_path=conf_path)
    if not cf.has_section(session):
        cf.add_section(session)
    cf.set(session, key, str(value))
    cf.write(open(conf_path, "w"))


def get_sessions(conf_path):
    '获取配置文件下所有session描述'
    cf = __generate_config_parser(conf_path=conf_path)
    return cf.sections()


def delete_session(conf_path, job_session):
    """删除session"""
    cf = __generate_config_parser(conf_path=conf_path)
    cf.remove_section(job_session)
    cf.write(open(conf_path, "w"))


def get_map_within_session(conf_path, session):
    """读取session下的所有键值对"""
    cf = __generate_config_parser(conf_path=conf_path)
    session_map = {}
    for session_item in cf.items(session):
        if session_item is not None:
            # utils_logger.log("[session_item]:",session_item)
            session_map[session_item[0]] = session_item[1]
    return session_map
