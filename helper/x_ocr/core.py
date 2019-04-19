#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import traceback

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)

import utils


def get_points_within_text(file_img, text_matcher, rect_limit=None):
    """
    查询图片中展示的坐标
    :param file_img: 
    :param text_matcher: 
    :param rect_limit:对于坐标的筛选过滤(TODO)
    :return: 
    """
    return utils.get_points_within_text(file_img=file_img, text_matcher=text_matcher)
