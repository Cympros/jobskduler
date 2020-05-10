# coding=utf-8

# 定义atx基本操作类

import uiautomator2 as u2

d = u2.connect("10.88.0.17:5555")
d.set_fastinput_ime(True)
s = d.session("com.netease.cloudmusic")
