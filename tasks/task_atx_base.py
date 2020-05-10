# coding=utf-8

# # atx使用文档
#
# 1.部署应用程序至手机端
# ```
# python -m uiautomator2 init
# ```
#
# 2.安装ATX Weditor，使用网页作为Inspector
# ```
# pip install --pre weditor
# ```
#
# 其他
# 1.参考文档：https://testerhome.com/topics/14880?locale=zh-TW
# import os
# try:
#     import uiautomator2 as u2
# except:
#     os.system('pip install  uiautomator2')
#     import uiautomator2 as u2
#
# d = u2.connect("10.88.0.17:5555")
# d.set_fastinput_ime(True)
# s = d.session("com.netease.cloudmusic")
print ('BBB')

if __name__ == '__main__':
    print ('AAA')