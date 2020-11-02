# coding=utf-8
# 发送邮件
import os
import sys
import json
import hashlib
import traceback

from numpy.core import unicode

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.insert(0, project_root_path)

from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from smtplib import SMTP_SSL
from smtplib import SMTPException

from helper import utils_common, utils_logger, utils_yaml
from helper import utils_file


def send_smtp_email(smtp_host, send_user, send_password, receiver_user, title, content, files, retry_count=3):
    utils_logger.log(smtp_host, send_user, send_password)
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
        smtp = login_if_possiable(smtp_host, send_user, send_password)
        # 发送邮件
        utils_logger.log("send_smtp_email base on [" + send_user + "]" + str(retry_count) + "] ...")
        smtp.sendmail(send_user, receiver_user, msg.as_string())
        return True
    except SMTPException:
        utils_logger.log("send_smtp_email重试索引[" + str(retry_count) + "]:", traceback.format_exc())
        if retry_count > 0:
            return send_smtp_email(smtp_host, send_user, send_password, receiver_user, title, content, files,
                                   retry_count - 1)
        else:
            return False


def login_if_possiable(smtp_host, user, password):
    smtp = SMTP_SSL(smtp_host)
    try:
        smtp.ehlo(smtp_host)
        smtp.login(user, password)
    except:
        utils_logger.log("login_if_possiable:", traceback.format_exc())
    return smtp


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
    file_first = root_path + '/tasks/appium/img/wc_jd_auth_confirm.png'
    wrapper_send_email(files=[file_first])
