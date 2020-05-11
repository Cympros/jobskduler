#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.insert(0, project_root_path)

# from helper import utils_image as ImageCutted
# from helper import utils_file as FileOperate
from x_aircv import utils as aircv_utils


class Template(object):
    """子图定位"""

    def __init__(self, file_name):
        self.file_path = os.path.abspath(file_name)
        self.threshold = 0.8
        self.rgb = None

    def find_all_matchs(self, template_parent):
        """搜索所有的匹配元素"""
        utils_logger.log("[find_all_matchs] starting...")
        parent_imread = template_parent.imread()
        cur_imread = self.imread()
        rets = []
        for method in ['sift', 'tpl']:
            utils_logger.log("[find_all_matchs] ", method)
            part_rets = None
            if method == "tpl":
                part_rets = self.find_templates_wrapper(parent_imread, cur_imread)
            elif method == "sift":
                part_rets = self.find_sifts_wrapper(parent_imread, cur_imread)
            else:
                utils_logger.log("找不到该适配模式", method)
                continue
            if part_rets is not None:
                rets.extend(part_rets)
        return rets

    def results_within_match_in(self, template_parent):
        """
        图片匹配,数组结构
        搜索当前图片在template_parent中的位置
        """
        parent_imread = template_parent.imread()
        cur_imread = self.imread()
        # 搜索cur_imread在parent_imread中的位置
        match_results = None
        for method in ['sift', 'tpl']:
            utils_logger.log("[Template]_cv_match:", method)
            if method == "tpl":
                match_results = self.find_templates_wrapper(parent_imread, cur_imread)
            elif method == "sift":
                match_results = self.find_sifts_wrapper(parent_imread, cur_imread)
            else:
                utils_logger.log("找不到该适配模式")
            # 检测搜索到的坐标是否合适
            if match_results is not None:
                utils_logger.log("ret is not None,break", match_results)
                break
        if match_results is None or len(match_results) == 0:
            utils_logger.log("none match result")
            return None
        utils_logger.log("results_within_match_in:", match_results)
        return match_results

    def find_templates_wrapper(self, imread_parent, imread_child, threshold=None, rgb=None):
        """图片匹配列表返回"""
        match_results = aircv_utils.find_templates(imread_parent=imread_parent, imread_child=imread_child)
        if match_results is not None:
            return match_results

        only_match = aircv_utils.find_only_template(imread_parent=imread_parent, imread_child=imread_child)
        if only_match is not None:
            return [only_match]
        return None

    def find_sifts_wrapper(self, imred_parent, imread_child, threshold=None, rgb=None):
        '''
        基于特征值搜索
        @:return [{'confidence':(*,*),'result':(*,*),'rectangle':[left-top,right-top,right-bottom,left-bottom]},{}]
        '''
        rets = aircv_utils.find_sifts(imread_parent=imred_parent, imread_child=imread_child)
        if rets is not None:
            return rets

        only_sift = aircv_utils.find_only_sift(imred_parent=imred_parent, imread_child=imread_child)
        if only_sift is not None:
            return [only_sift]
        return None

    def imread(self):
        utils_logger.log("_imread:", self.file_path)
        return aircv_utils.imread(self.file_path)


if __name__ == '__main__':
    file = root_path + 'test/screen_shot_jingdou_peiyucang.png'
    cutted_file_path = FileOperate.generate_suffix_file(file, suffix="cutted")
    child_template = Template(
        ImageCutted.cutted_image_with_scale(raw_file_path=file, cutted_save_file_path=cutted_file_path,
                                            cutted_rect_scale=[0.33, 0.66, 0.4, 0.6]))
    parent_template = Template(file)  # 这里的parenr_template一般使用截图文件
    query_results = child_template.results_within_match_in(parent_template)
    utils_logger.log("result for test:", query_results)
