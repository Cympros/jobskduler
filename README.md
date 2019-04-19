# 自动化脚本方案优劣对比
1.基于appium方式：脚本方便，但需要额外的移动手持设备  
2.基于selenium类似方案：需要下载浏览器驱动程序，且启动速度慢  

# job_schduler的使用方法
1.添加job任务   
```
仿照./common/job.config类似配置   
```
2.开启后台服务
```
bash extra/job_scheduler/schduler_terminal_controller.sh
```

# appium类型任务小技巧
1.查看手机上当前的Activity
```
    //first:清空后台应用
    adb shell dumpsys activity top | grep ACTIVITY
```
2.查看当前页面元素
2.1 Native页面：
    命令行输入"uiautomatorviewer"启用Andorid自带View视图查看工具
    注：
    1.Error obtaining UI hierarchy  Reason:Error while obtaining UI hierarchy XML file.com.android.ddmlb.SynchException.Remote object doesn't exist.
        调用该命令时请确保appium是关闭的
        参考链接：https://stackoverflow.com/questions/25201743/error-in-using-uiautomatorviewer-for-testing-android-app-in-appium
2.2 WebView布局：
3.需要通过坐标定位的情况
    开发者选项 ---> 显示指针位置，勾选即可
4.微信H5调试技巧
```
* 访问"http://debugx5.qq.com" 
* 点击'信息'
* 勾选'打开TBS内核Inspector调试功能'
* Google访问'chrome://inspect/#devices'
```






问题
1.若提示"import module"找不到，可以在import下方调用"print locals()"方法以打印当前引用的包名路径，以此check

# TODO
1.解析xml文件，获取对应node的下标：可用于包装appium框架，自己使用page_resource配合自我解析point来解决      
4.方案研究：driver.find_element_by_android_uiautomator("new UiSelector().className(" + class_name + ").text(" + text + ")")  
7.基于charles分析请求链接，然后拼接请求url完成操作请求
8.测试框架封装示例：https://testerhome.com/topics/6247
9.直接api访问执行京东签到领京豆任务：sign_url = 'https://api.m.jd.com/client.action?functionId=signBeanStart'
12.校验query_wrapper中element的有效区域
13.任务添加执行时间间隔，以屏蔽无效执行
记录每个job调用query_point的次数，以便后续持续优化
1.driver.switch_to.context之后都要做一遍当前context是否切换成功的校验  另：switch之前判断context是否已经是指定contexts
2.airtest macaca
1.npm安装速度慢  npm install -g macaca-cli --registry=https://registry.npm.taobao.org
邮件：分辨率提供    搜索到的element的坐标    京东每日福利任务-关闭   高优先级判断  
判断图片文件格式是否合法    时间显示在########
惠锁屏打卡按钮识别为空
http://ai.baidu.com/docs#/OCR-API/0d9adafa
