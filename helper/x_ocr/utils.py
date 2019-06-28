#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import uuid
import time
import urllib2
import random
import base64
import urllib
import hashlib
import requests
import traceback
from requests.exceptions import ConnectionError
from aip import AipOcr

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)

from helper import utils_common, utils_logger


def query_all_ocrs_throw_ocr(file_img):
    """返回所有的ocr识别记录"""
    results = None
    status = False
    for ocr_type in ['baidu', 'youdao', 'tencent', 'xunfei']:
        if ocr_type == 'baidu':
            status, results = _query_ocr_by_baiduapi(file_img=file_img)
        elif ocr_type == 'youdao':
            status, results = _query_ocr_by_youdao(file_img=file_img)
        # elif ocr_type == 'tencent':
        #     status,results=_query_ocr_by_tencentapi(file_img=file_img)
        elif ocr_type == 'xunfei':
            status, results = _query_ocr_by_xunfei(file_img=file_img)
        if status is True:
            utils_logger.log("---> start query in ocr_type:", ocr_type)
            break
    return results


def get_points_within_text(file_img, text_matcher):
    '搜索文字在图片中的位置'
    "解决中文匹配问题：r'家[\x80-\xff]{3}年中盛典' 可搜索到'家电年中盛典'，适用于单个中文字符匹配"
    "location以左上角坐标+宽高的方式返回"
    query_results = query_all_ocrs_throw_ocr(file_img=file_img)
    if query_results is None:
        return None
    matched_results = []
    for ocr_item in query_results:
        utils_logger.log("---> get_points_within_text:'" + text_matcher + "' vs '" + str(ocr_item['words']) + "'")
        if re.match(text_matcher, str(ocr_item['words'])) is None:  # 正则匹配失败,这里需要注意str转换，否则match失效
            continue
        utils_logger.log(ocr_item)
        matched_results.append(ocr_item)
    return matched_results


def _query_ocr_by_baiduapi(file_img):
    '基于百度文字识别的方案'
    '参考文档:https://cloud.baidu.com/doc/OCR/OCR-Python-SDK.html#.E5.BF.AB.E9.80.9F.E5.85.A5.E9.97.A8'
    config = {
        'appId': '11455806',
        'apiKey': 'NZ5gYFoGoRW75Gr737Yy440O',
        'secretKey': 'OnZXqj4O18i6b7hd9SRvyPswcuFNxCDA'
    }
    client = AipOcr(**config)
    image = utils_common.get_file_content(file_img)
    options = {"vertexes_location": "true"}
    try:
        result = client.general(image, options)
    except ConnectionError:
        utils_logger.log(traceback.format_exc())
        return False, None
    except Exception:
        utils_logger.log(traceback.format_exc())
        return False, None
    if 'words_result' not in result:
        utils_logger.log("get_point_within_text_by_baiduaip failed",
                         json.dumps(result, encoding='utf-8', ensure_ascii=False))
        return False, None
    query_points = []
    for word_item in result['words_result']:
        if 'words' not in word_item:
            continue
        # 下面判断需要顶部sys.setdefaultencoding的配合生效，否者会提示'ascii' codec can't encode characters in position 0-7: ordinal not in range(128)'
        point = {'location': word_item['location'], 'words': word_item['words']}
        point_x = int(word_item['location']['left']) + random.randint(0, int(word_item['location']['width']))
        point_y = int(word_item['location']['top']) + random.randint(0, int(word_item['location']['height']))
        point['avaiable_point'] = (point_x, point_y)
        query_points.append(point)
    # utils_logger.log("_get_points_within_text_by_baiduapi", json.dumps(query_points, encoding='utf-8', ensure_ascii=False)
    return True, query_points


def _query_ocr_by_youdao(file_img):
    '有道智云OCR服务：http://ai.youdao.com/docs/doc-ocr-api.s#p02'
    api = 'https://openapi.youdao.com/ocrapi'
    img_base64 = base64.b64encode(utils_common.get_file_content(file=file_img))
    app_key = '613c6f05502f3925'
    app_pwd = 'xtiSvfpXWqtOD6E6azlh226cmVuWw2TN'
    salt = str(uuid.uuid1())

    hl = hashlib.md5()
    sign_raw = app_key + img_base64 + salt + app_pwd
    hl.update(sign_raw.encode(encoding='utf-8'))
    sign = hl.hexdigest().upper()  # md5化并大写
    request_param = {'img': img_base64, 'langType': 'zh-en', 'detectType': '10012', 'imageType': '1', 'appKey': app_key,
                     'salt': salt,
                     'docType': 'json', 'sign': sign}
    try:
        # ConnectionError: ('Connection aborted.', error(104, 'Connection reset by peer'))
        response = json.loads(requests.post(api, data=request_param).text)
    except ConnectionError:
        utils_logger.log(traceback.format_exc())
        return False, None
    if 'Result' not in response:
        utils_logger.log("request failed with no Result", response)
        return False, None
    if 'regions' not in response['Result']:
        utils_logger.log("request failed with no regions", response)
        return False, None

    utils_logger.log("---> _get_points_within_text_by_youdao")
    query_points = []
    for parase_item in response['Result']['regions']:
        if 'text' in parase_item:
            utils_logger.log("---> regions:", parase_item['text'])
        if 'lines' not in parase_item:
            utils_logger.log("---> not need to anylaze in lines", parase_item)
            continue
        for line_item in parase_item['lines']:
            if 'text' not in line_item:
                utils_logger.log("---> not need to anylaze in line_item", line_item)
                continue
            # utils_logger.log(line_item
            # 先将字符串按照','切片，并将切片后每个字符串item转成int类型
            point_tmp_list = list(map(int, re.split(',', line_item['boundingBox'])))
            if len(point_tmp_list) != 8:
                utils_logger.log("--> boundingBox size not right", line_item)
                continue
            point = {'words': line_item['text']}
            # 获取行位置的下标信息
            point_left = int(min(point_tmp_list[::2]))  # 偶数项
            point_top = int(min(point_tmp_list[1::2]))  # 奇数项
            width = int(max(point_tmp_list[::2])) - point_left
            height = int(max(point_tmp_list[1::2])) - point_top
            point['location'] = [point_left, point_top, width, height]
            # 给出可用的point
            point_x = point_left + random.randint(0, width)
            point_y = point_top + random.randint(0, height)
            point['avaiable_point'] = (point_x, point_y)

            query_points.append(point)
    return True, query_points


def _query_ocr_by_tencentapi(file_img):
    '''
        TODO:老是提示签名错误
        https://ai.qq.com/doc/ocrgeneralocr.shtml
    '''
    utils_logger.log('--->_get_point_within_text_tencentapi')
    api = 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr'

    # raw_request_param必须搜按照key升序排列
    request_param = {'app_id': 2108799585,
                     'image': base64.b64encode(utils_common.get_file_content(file=file_img)),
                     'nonce_str': "ddbbvsvsdsvvwv",
                     'sign': "",
                     'time_stamp': int(time.time())}
    # 鉴权
    request_str = ""
    for value in [(k, request_param[k]) for k in sorted(request_param.keys())]:
        if value[1] == "":
            continue
        utils_logger.log(value[0])
        request_str = request_str + value[0] + '=' + urllib.quote(str(value[1])) + '&'
        # utils_logger.log(value[0]
    # utils_logger.log(request_str
    request_str = request_str + 'app_key=' + 'X74khf5HkW058XtO'
    # utils_logger.log(request_str
    sign_value = hashlib.md5(request_str).hexdigest().upper()
    utils_logger.log("--->sign_value：", sign_value)

    request_param['sign'] = sign_value
    # request_str=request_str+"&sign="+sign_value
    # utils_logger.log(request_str
    # utils_logger.log(request_param

    response = json.loads(requests.post(api, data=request_param).text)
    utils_logger.log(response)


def _query_ocr_by_xunfei(file_img):
    """
    讯飞Ocr文字识别
    https://www.xfyun.cn/services/textRecg
    """
    api_key = '0bdcee17a3d533c6bf2a291438b7682c'  # api_key
    x_appid = "5bc5af2f"  # appid

    base64_image = base64.b64encode(open(file_img, 'rb').read())
    body = urllib.urlencode({'image': base64_image}).encode(encoding='utf-8')
    url = 'http://webapi.xfyun.cn/v1/service/v1/ocr/general'
    param = {"language": "cn|en", "location": "true"}

    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode(encoding="utf-8"))
    x_param_b64_str = x_param.decode('utf-8')
    x_time = str(int(int(round(time.time() * 1000)) / 1000))
    string = (api_key + x_time + x_param_b64_str).encode('utf-8')
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param_b64_str,
                'X-CheckSum': hashlib.md5(string).hexdigest()}
    # 发送网络请求
    req = urllib2.Request(url, body, x_header)
    # 开始解析数据
    try:
        result = urllib2.urlopen(req).read()
        data = json.loads(result).get('data').get('block')
        for block in data:
            if block.get('type') == 'text':
                data = block
    except:
        utils_logger.log(traceback.format_exc())
        return False, None
    # ocr_results
    query_points = []
    for line in data.get('line'):
        words = line.get('word')
        for word in words:
            content = word.get('content')
            if content is None or content == '':
                continue
            location = word.get('location')
            point = {'words': content}
            left = int(location.get('top_left').get('x'))
            top = int(location.get('top_left').get('y'))
            right = int(location.get('right_bottom').get('x'))
            bottom = int(location.get('right_bottom').get('y'))
            point['location'] = [left, top, right - left, bottom - top]
            # 给出可用的point
            point_x = random.randint(left, right)
            point_y = random.randint(top, bottom)
            point['avaiable_point'] = (point_x, point_y)

            utils_logger.log("--->[_get_points_within_text_by_xunfei]", content, " - ", point)
            query_points.append(point)
    return True, query_points


if __name__ == '__main__':
    # TODO:不要在接口请求中过滤结果
    test_status, test_results = _query_ocr_by_baiduapi(
        "../test/job_scheduler_out_screen_tmp_600x1024_double_quqiandao.png")
    if test_status is True:
        for item in test_results:
            utils_logger.log(item['words'], "---> ", item)
