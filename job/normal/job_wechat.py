# coding=utf-8

import itchat
import thread
import time
import os
import sys
import random
import json
from itchat.content import *

reload(sys)
sys.setdefaultencoding('utf-8')

from job_base import BaseJob as Base

common_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../common')
# utils_logger.log("---> common path is: ",common_path
sys.path.append(common_path)
import email_send
from helper import utils_logger
import env_job
import utils


# 扫描qr的回调函数
class QR_Callback:
    def __init__(self, uuid, status, qrcode):
        file_path = "QR.png"
        # itchat.get_QR(enableCmdQR=True)
        with open(file_path, 'wb') as f:
            f.write(qrcode)
        # 邮件通知用户登录服务器扫描二维码
        email_send.wrapper_send_email(title=u'微信二维码登录请求', content='请用微信扫描下述二维码', files=file_path)

    # 用于itchat模块判断是否是回调函数，具体查看login.py的
    # if hasattr(loginCallback, '__call__'):
    # 部分
    def __call__(self, *args, **kwargs):
        return self


# 定义与微信模块调用相关的东西
class JobWechat(Base):
    wechat_job = None

    def __init__(self, send_message, is_need_listen_callback=True):
        Base.__init__(self)
        self.need_still_listen = False
        self.send_message = send_message
        self.target_user = None
        self.is_need_listen_callback = is_need_listen_callback  # 是否需要监听回复消息
        # 可能收到多条回复的逻辑
        self.max_check_reply_count = 10
        self.has_check_reply_count = 0

    # 处理收到的消息
    def deal_reply_msg(self, msg):
        utils_logger.log("---> deal_reply_msg in thread")

    # 所有消息的回调都会走这里
    def whole_reply(self, msg):
        if self.target_user is None:
            # 屏蔽缓存信息
            return
        if msg['FromUserName'] != self.target_user:
            utils_logger.log("接收到非目标用户的消息，舍弃")
            return
        global wechat_job
        if wechat_job is None:
            utils_logger.log("---> wechatjob not defined")
            return
        if not self.need_still_listen:
            utils_logger.log("---> 已经放弃监听reply信息")
            return
        # 检查是否是需要的回复
        is_reply_legal = wechat_job.check_reply(msg)
        if not is_reply_legal:
            # 仅当收到的有效回复数大于阈值时，才邮件通知解决
            if self.has_check_reply_count >= self.max_check_reply_count:
                # 调用基类方法收集错误日志
                wechat_job.job_scheduler_failed(message=msg)
            self.has_check_reply_count = self.has_check_reply_count + 1
        else:
            # 已经收到有效回复，停止循环监听
            self.need_still_listen = False
            self.notify_job_success()
            self.deal_reply_msg(msg=msg)
            # thread.start_new_thread(self.deal_reply_msg, (msg,))  # msg后必须添加逗号

    def __check_reply_msg(self):
        # utils_logger.log("---> __check_reply_msg"

        # 这里的TEXT表示如果有人发送文本消息，那么就会调用下面的方法
        @itchat.msg_register(TEXT)
        def simple_text_reply(msg):
            global wechat_job
            wechat_job.whole_reply(msg)

        @itchat.msg_register(SHARING, isFriendChat=True, isGroupChat=True, isMpChat=True)
        def link_reply(msg):
            global wechat_job
            wechat_job.whole_reply(msg)

    # 获取目标用户标识
    def get_target_user(self):
        return None

    # 检查是否是有效回复
    def check_reply(self, msg):
        return False

    def run_task(self):
        global wechat_job
        wechat_job = self

        # 判断是否还需要持续监听reply信息
        self.need_still_listen = True

        # 自动登录
        itchat.auto_login(hotReload=True, enableCmdQR=True, qrCallback=QR_Callback,
                          statusStorageDir=env_job.get_out_dir() + "/itchat.pkl")

        _target_user = self.get_target_user()
        if _target_user is None:
            utils_logger.log("---> not found target_user,force exit")
            return

        utils_logger.log(u'---> 开启itchat轮训线程')
        thread.start_new_thread(itchat.run, ())

        random_time = random.randrange(10, 35)
        utils_logger.log(u'---> itchat指令发送 prepare', ' with delay of ', random_time, '...')
        time.sleep(random_time)  # 延迟调用send函数，避免被微信封禁

        utils_logger.log(u'---> itchat指令发送 start...')
        self.target_user = _target_user
        itchat.send(self.send_message, self.target_user)

        # 轮训查询回复的消息内容
        check_period = 1  # 几秒轮训一次
        runned_max_count = 400  # 最多等待400*check_period秒
        run_index = 0
        while True:
            if not self.is_need_listen_callback:
                utils_logger.log("---> 不需要监听回调")
                break
            if run_index > runned_max_count:
                self.job_scheduler_failed('指令reply程序检测次数超出上限，exit')
                break
            if not self.need_still_listen:
                utils_logger.log("---> 指令程序状态执行成功，exit")
                break
            self.__check_reply_msg()
            time.sleep(check_period)
            run_index = run_index + 1


class WechatSqjyxzsSign(JobWechat):
    def __init__(self):
        JobWechat.__init__(self, u'签到')

    def get_target_user(self):
        friendslist = itchat.search_friends(u'省钱小助手-淘宝')
        if len(friendslist) != 1:
            utils_logger.log("---> 获取到的朋友不唯一，exit")
            self.job_scheduler_failed(friendslist)
            return None
        return friendslist[0]["UserName"]

    def check_reply(self, msg):
        # msg['Type']
        reply_msg = json.dumps(msg['Content'], encoding='utf-8', ensure_ascii=False)
        utils_logger.log("---> check_reply：", reply_msg)
        if reply_msg.find(u'今天已经签到过了，明天再来哦') or reply_msg.find(u'签到成功'):
            return True
        else:
            return False


class WechatCreditcardRepayState(JobWechat):
    def __init__(self):
        JobWechat.__init__(self, u'账单')

    def query_similary_list(self, target, lists):
        result = []
        for item in lists:
            if item.find(target) != -1:
                result.append(item)
        return result

    def get_target_user(self):
        friendslist = itchat.search_mps(u'招商银行信用卡')
        if len(friendslist) != 1:
            utils_logger.log("---> 获取到的朋友不唯一，exit")
            self.job_scheduler_failed(friendslist)
            return None
        return friendslist[0]["UserName"]

    def deal_reply_msg(self, msg):
        JobWechat.deal_reply_msg(self, msg)
        reply_msg = json.dumps(msg['Content'], encoding='utf-8', ensure_ascii=False)
        fliters = list(set(reply_msg.split(r'\n\n')))  # 双换行符分割并去重
        renmingbi_strs = self.query_similary_list("人民币账单", fliters)
        if len(renmingbi_strs) != 1:
            self.job_scheduler_failed("not found '人民币账单'相关信息")
            return
        else:
            if renmingbi_strs[0].find(u'您的人民币账单已还清') != -1:
                utils_logger.log("账单已还清，不需要额外处理")
                return
            else:
                utils_logger.log("发送邮件提示信用卡还款")
                email_send.wrapper_send_email(title=u'信用卡还款', content="请检查信用卡还款状态")

    def check_reply(self, msg):
        reply_msg = json.dumps(msg['Content'], encoding='utf-8', ensure_ascii=False)
        utils_logger.log("---> check_reply:", reply_msg)
        find_state = reply_msg.find(u'个人信用卡账单')
        if find_state != -1:
            # utils_logger.log(reply_msg
            return True
        return False


class WechatZhaoshangCreditcardSign(JobWechat):
    def __init__(self):
        JobWechat.__init__(self, "签到")

    def get_target_user(self):
        friendslist = itchat.search_mps(u'招商银行信用卡')
        if len(friendslist) != 1:
            utils_logger.log("---> 获取到的朋友不唯一，exit")
            self.job_scheduler_failed(friendslist)
            return None
        return friendslist[0]["UserName"]

    def check_reply(self, msg):
        reply_msg = json.dumps(msg['Content'], encoding='utf-8', ensure_ascii=False)
        if reply_msg.find(u'叮~签到成功！您获得') != -1:
            return True
        elif reply_msg.find(u'亲~您今天已经签过到啦！回复“我的签到”可查看明细哦') != -1:
            return True
        else:
            self.job_scheduler_failed(reply_msg)
            return False


class WechatKeepAliveChecker(JobWechat):
    '用来检测wechat是否在线的模块'

    def __init__(self):
        JobWechat.__init__(self, send_message="hell world," + str(utils.get_shanghai_time('%Y%m%d %H:%M:%S')),
                           is_need_listen_callback=False)

    def get_target_user(self):
        friendslist = itchat.search_friends(u'Jimmie')
        if len(friendslist) != 1:
            utils_logger.log("---> 获取到的朋友不唯一，exit")
            self.job_scheduler_failed(friendslist)
            return None
        return friendslist[0]["UserName"]


if __name__ == "__main__":
    tasks = ['WechatCreditcardRepayState', 'WechatZhaoshangCreditcardSign', 'WechatKeepAliveChecker',
             'WechatSqjyxzsSign']
    while True:
        input_info = "------------------------执行任务列表-----------------------\n"
        for index, task_item in enumerate(tasks):
            input_info += str(index) + "：" + task_item + "\n"
        task_index_selected = raw_input(input_info + "请选择需运行任务对应索引(索引下标越界触发程序退出)：")
        if task_index_selected.isdigit() is False:
            utils_logger.log("索引值非数字，请重新输入：", task_index_selected)
            continue
        task_index_selected = int(task_index_selected)
        if task_index_selected >= len(tasks) > 0:
            utils_logger.log("[" + str(task_index_selected) + "]任务索引不存在，退出程序...")
            break
        task_name = tasks[task_index_selected]
        job = eval(task_name + '()')
        job.run_task()
