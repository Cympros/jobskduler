#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    import aircv
except:
    os.system('pip install opencv-python --default-timeout=10000')
    import aircv
import traceback

# from airtest import aircv as airtest_aircv

project_root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(project_root_path)

def imread(file_path):
    return aircv.imread(file_path)


def find_only_template(imread_parent, imread_child):
    return aircv.find_template(imread_parent, imread_child)


def find_templates(imread_parent, imread_child):
    return aircv.find_all_template(imread_parent, imread_child)


def find_only_sift(imred_parent, imread_child, threshold=None, rgb=None):
    """基于特征值单个搜索"""
    utils_logger.log("--->find_only_sift")
    try:
        match_result = aircv.find_sift(imred_parent, imread_child)
        if match_result is not None:
            return match_result
    except Exception:
        utils_logger.log("--->[find_only_sift] faile with caught exception")
        utils_logger.log(traceback.print_exc())
    return None


def find_sifts(imread_parent, imread_child, threshold=None, rgb=None):
    """基于特征值批量搜索"""
    # TODO:Assertion failed: (queries.cols == veclen()), function knnSearch, file /Users/travis/build/skvark/opencv-python/opencv/modules/flann/include/opencv2/flann/nn_index.h, line 70.
    # utils_logger.log("--->_find_sifts"
    # try:
    #     match_results=aircv.find_all_sift(imread_parent, imread_child, maxcnt = 20)
    #     if match_results is not None:
    #         return match_results
    # except:
    #     utils_logger.log(traceback.print_exc()
    return None


def find_sift_in_predict_area(imread_parent, imread_child):
    utils_logger.log("--->find_sift_in_predict_area")
    # image_wh, screen_resolution = airtest_aircv.get_resolution(imread_child), airtest_aircv.get_resolution(imread_parent)
    # utils_logger.log("--->**************",image_wh,screen_resolution
    return None
    # if not self.record_pos:
    #     return None
    # # calc predict area in screen
    # image_wh, screen_resolution = aircv.get_resolution(image), aircv.get_resolution(screen)
    # xmin, ymin, xmax, ymax = Predictor.get_predict_area(self.record_pos, image_wh, self.resolution, screen_resolution)
    # # crop predict image from screen
    # predict_area = aircv.crop_image(screen, (xmin, ymin, xmax, ymax))
    # if not predict_area.any():
    #     return None
    # # find sift in that image
    # ret_in_area = aircv.find_sift(predict_area, image, threshold=self.threshold, rgb=self.rgb)
    # # calc cv ret if found
    # if not ret_in_area:
    #     return None
    # ret = deepcopy(ret_in_area)
    # if "rectangle" in ret:
    #     for idx, item in enumerate(ret["rectangle"]):
    #         ret["rectangle"][idx] = (item[0] + xmin, item[1] + ymin)
    # ret["result"] = (ret_in_area["result"][0] + xmin, ret_in_area["result"][1] + ymin)
    # return ret

# def imread(filename):
#     """根据图片路径，将图片读取为cv2的图片处理格式."""
#     if not os.path.isfile(filename):
#         raise Exception("File not exist: %s" % filename)
#     if PY3:
#         stream = open(filename, "rb")
#         bytes = bytearray(stream.read())
#         numpyarray = numpy.asarray(bytes, dtype=numpy.uint8)
#         img = airtest_aircv.imdecode(numpyarray, airtest_aircv.IMREAD_UNCHANGED)
#     else:
#         filename = filename.encode(sys.getfilesystemencoding())
#         img = airtest_aircv.imread(filename)
#     return img
