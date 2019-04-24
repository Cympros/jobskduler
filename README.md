# job_schduler模块简单使用
1.添加job任务定义     
具体可参考"./config/job.config"中结构申明
```
[job_wechat.WechatZhaoshangCreditcardSign]      //必填项：以"python文件名.class名称"
job_name = 招行信用卡微信签到        //任务名称描述
runnable = false        //任务是否启用(总控开关)。另，也可通过其他条件灵活控制任务是否执行(详见job_base.py文件)
```
2.自定义任务     
所有任务类均继承至"./job/job_base.py#BaseJob"      
function:run_task：任务执行入口类       
补充：     
```
./job/appium/helper/job_appium_base.py：appium类型任务的基类封装      
```
2.1 appium任务支持功能
```
1.appium服务端口自动创建机制
2.appium参数配置自动化检测
3.锁屏模式下自动解锁(仅支持'未设备密码'情况)
4.appium下element检索模式封装(viewid、text、xpath等)
5.支持appium.findElementByxxx()下的重试
6.支持子图识别定位
7.支持网页等待页面(即'正在加载中'页面)识别
8.ocr文字识别定位
9.单击事件响应封装(element.click()以及point.tab())
10.异常信息上送(详见job_scheduler_failed方法实现)
```
3.任务执行
```
bash ./schduler_terminal_controller.sh
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
4.微信H5调试技巧
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
