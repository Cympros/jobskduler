# 导出pip依赖信息
pip freeze > requirements.txt
pip install -r requirements.txt

# daily-task支持功能简介
1.支持功能说明
```
1.appium服务端口可用性检测机制
2.appium参数配置自动化检测
3.锁屏模式下自动解锁(仅支持'未设备密码')
4.appium下element检索模式封装(viewid、text、xpath等)
5.支持appium.findElementByxxx()重试机制
6.支持子图识别定位
7.支持网页等待页面(即'正在加载中'页面)识别:基于空白比例判断
8.ocr文字识别定位
9.单击事件响应封装(element.click()以及point.tab()):判断是否clickable
10.异常信息上送(详见job_scheduler_failed方法实现)
```
2.运行方式
```
python tasks_schduler_core.py
```
注：      
3.1 Mac由于休眠状态下会暂停所有任务，后测试发现通过"screen"方式启动任务即使休眠状态依旧可执行

# 自动化脚本方案优劣对比
1.基于appium方式：脚本方便，但需要额外的移动手持设备  
2.基于selenium类似方案：需要下载浏览器驱动程序，且启动速度慢  


# 查看当前页面元素
1.Native页面：
```
uiautomatorviewer   //命令行输入该命令即启用Andorid自带View视图查看工具
```
1.1 异常错误    
1.1.0 Error obtaining UI hierarchy  Reason:Error while obtaining UI hierarchy XML file.com.android.ddmlb.SynchException.Remote object doesn't exist.    
解决方案：确认确保appium服务是关闭状态  
参考链接：https://stackoverflow.com/questions/25201743/error-in-using-uiautomatorviewer-for-testing-android-app-in-appium

2.需要通过坐标定位的情况
```
开发者选项 ---> 显示指针位置，勾选即可
```
3.微信H5调试技巧
```
* 访问"http://debugx5.qq.com" 
* 点击'信息'
* 勾选'打开TBS内核Inspector调试功能'
* Google访问'chrome://inspect/#devices'
```


# 项目中遇到的问题     
1.提示"import module"找不到
可以在import下方调用"print locals()"方法以打印当前引用的包名路径，以此check     


# TODO
1.解析xml文件，获取对应node的下标：可用于包装appium框架，自己使用page_resource配合自我解析point来解决      
2.方案研究：driver.find_element_by_android_uiautomator("new UiSelector().className(" + class_name + ").text(" + text + ")")  
3.基于charles分析请求链接，然后拼接请求url完成操作请求   
4.测试框架封装示例：https://testerhome.com/topics/6247   
5.直接api访问执行京东签到领京豆任务：sign_url = 'https://api.m.jd.com/client.action?functionId=signBeanStart'   
6.airtest macaca      
7.http://ai.baidu.com/docs#/OCR-API/0d9adafa  
8.self.dos.excute_cmd('taskkill -F -PID node.exe')使用
9.参数补全："appium -p "+4723 + "-bp "+4900 +" --no-reset --session-override -log D:/log/myd.log"
10.thread被打断后自动重启
11.基于'netstat -ano | findstr '+str(port_num)判断appium服务端口是否被占用
12.appium:appWaitActivity配置的使用


install_if_not_exist 'timeout' 'brew install coreutils && sudo ln -s /usr/local/bin/gtimeout /usr/local/bin/timeout'

# 关闭appium进程
utils_common.exec_shell_cmd('''ps -ef | grep "appium" | grep -v -E "grep|$$" | awk  '{print "kill -9 " $2}' | sh''')


                device_thread = threading.Thread(target=device_thread_loop,
                                                 args=(job_infos),
                                                 name=thread_name)
                # 设置为后台线程，这样主线程结束时能自动退出
                device_thread.setDaemon(True)
                device_thread.start()




                `tesseract <img_path> <img_tesseract_result_name> -l chi_sim -psm 6 makebox`
                -l <lang>
                # 设置识别语言类型，支持多种语言混合识别(即lang用+链接)
                另，查看支持语言可通过调用`tesseract --list-langs`
                官方支持语言：https://github.com/tesseract-ocr/tessdata
                新增支持语言：将*.traineddata拷贝至/usr/local/Cellar/tesseract/3.05.02/share/tessdata/
                -psm
                # 识别图像的方式
                具体支持类型可使用`tesseract --help-psm`查看
                makebox
                # 输出坐标信息