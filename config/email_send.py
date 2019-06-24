# coding=utf-8
# 发送邮件
import os
import sys
import json
import hashlib
import traceback

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)

from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import encoders

from smtplib import SMTP_SSL
from smtplib import SMTPException

from helper import utils_common, utils_logger
from helper import utils_file

# 上次发送邮件Msg的md5标识,新增批量文件的综合标识
last_email_files_md5 = None


def wrapper_send_email(title=None, content=None, files=None):
    mail_title = title if title is not None else u'python邮件标题'
    # files组合成数组
    wrapper_files = None
    if files is not None:
        if not isinstance(files, list):
            wrapper_files = [files]
        else:
            wrapper_files = files
    # 组装邮件内容[Git_Desc下格式]：【local分支】+【git_revision_number】+【orgin信息】+【commit_desc】
    mail_content = "Device_Host_Name:  " + utils_common.get_host_name() + "\n" \
                   + "Host_IP:   " + utils_common.get_real_host_ip() + "\n" \
                   + "Git_Desc:   " + json.dumps(utils_common.exec_shell_cmd("git branch -vv | grep '*'"),
                                                 ensure_ascii=False, ) + "\n\n" \
                   + "Content:    \n" + (content if content is not None else '来自python登录qq邮箱的测试邮件')
    # 校验重复发送:保存当前文件集的md5标识
    global last_email_files_md5
    this_email_file_md5 = get_files_md5(wrapper_files)
    if last_email_files_md5 is not None:
        if last_email_files_md5 == this_email_file_md5:  # check msg的md5标识，以检测是否需要重复发送
            return
        else:
            utils_logger.log("---> ", this_email_file_md5, " vs ", last_email_files_md5)
    last_email_files_md5 = this_email_file_md5

    raise Exception("请根据个人情况修改下方包含'***'部分内容.....")
    # # 发送邮件
    # receiver_user = '<****邮件接收地址>'  # 邮件接收地址
    # utils_logger.append_log("---> start to wrapper_send_email[" + receiver_user + "][" + mail_title + "]:",
    #                         wrapper_files)
    # email_state = send_smtp_email('smtp.163.com', '<***发送者163邮箱地址>', '<****发送方邮箱密码>',
    #                               receiver_user, mail_title, mail_content, wrapper_files)
    # if email_state is False:
    #     utils_logger.append_log("---------------------wrapper_send_email caught exceptiion---------------------------")


def send_smtp_email(smtp_host, send_user, send_password, receiver_user, title, content, files, retry_count=3):
    try:
        # 构造邮件
        msg = MIMEMultipart()
        msg["Subject"] = Header(title, 'utf-8')
        msg["From"] = _format_addr(u'埃德温·贾维斯 <%s>' % send_user)
        msg["To"] = receiver_user
        msg.attach(MIMEText(content, "plain", 'utf-8'))  # 用下方方式可将附件加在正文当中显示
        if files is not None:
            for file_item in files:
                mime = mk_file_mime(file_item)
                if mime is None:
                    continue
                msg.attach(mime)  # 添加到MIMEMultipart
        # ssl登录
        smtp = SMTP_SSL(smtp_host)
        smtp.ehlo(smtp_host)
        smtp.login(send_user, send_password)
        # 发送邮件
        utils_logger.append_log("---> send_smtp_email base on [" + send_user + "]" + str(retry_count) + "] ...")
        smtp.sendmail(send_user, receiver_user, msg.as_string())
        return True
    except SMTPException:
        utils_logger.append_log("send_smtp_email重试索引[" + str(retry_count) + "]:", traceback.format_exc())
        if retry_count > 0:
            return send_smtp_email(smtp_host, send_user, send_password, receiver_user, title, content, files,
                                   retry_count - 1)
        else:
            return False


# 构造file集合的md5标识，该方法是针对邮件去重增加的算法
def get_files_md5(files):
    if files is None:
        return None
    file_md5s = []
    for file_item in files:
        file_itme_md5 = utils_common.get_file_md5(file_item)
        if file_itme_md5 is None:
            continue
        file_md5s.append(file_itme_md5)
    file_md5s.sort()  # 针对存放md5标识的数组先排序
    # 对md5的数组进行md5标识
    files_hash = hashlib.md5()
    files_hash.update(" ".join(file_md5s))  # 数组先转成string再获取md5标识
    return files_hash.hexdigest()


# 格式化邮件地址
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


# 根据filenameMIMEBase
def mk_file_mime(file_path):
    if file_path is None or os.path.exists(file_path) is False:
        return None
    with open(file_path, 'rb') as f:
        # 设置附件的MIME和文件名，这里是png类型:
        mime = MIMEBase('image', 'png', filename=utils_file.get_file_name_by_file_path(file_path))
        # 加上必要的头信息:
        mime.add_header('Content-Disposition', 'attachment', filename=utils_file.get_file_name_by_file_path(file_path))
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        # 把附件的内容读进来:
        mime.set_payload(f.read())
        # 用Base64编码:
        encoders.encode_base64(mime)
    return mime


if __name__ == "__main__":
    file_first = root_path + '/job/appium/img/wc_jd_auth_confirm.png'
    wrapper_send_email(files=[file_first])
