# coding=utf-8

import os
import sys

project_root_path = os.path.abspath(os.path.split(os.path.realpath(__file__))[0] + '/../../../')
sys.path.insert(0, project_root_path)

# from helper import utils_common, utils_logger
from helper import envs
from tasks.appium.task_appium_base import BasicAppiumTask

'需要重新绑定账号：13651968735'


class TaskAppiumZhuankeBase(BasicAppiumTask):
    def __init__(self):
        BasicAppiumTask.__init__(self)

    def run_task(self):
        return BasicAppiumTask.run_task(self)

    def except_case_in_query_ele(self):
        if BasicAppiumTask.except_case_in_query_ele(self) is True:
            return True
        # self.query_ele_wrapper(self.get_query_str_by_viewid('cn.zhuanke.zhuankeAPP:id/dialog_title'),is_ignore_except_case=True,retry_count=0) is not None 
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text("新版本升级"),
                                  is_ignore_except_case=True,
                                  retry_count=0) is not None:
            # 检测到升级逻辑，点击取消逻辑
            if self.query_ele_wrapper("#viewid#cn.zhuanke.zhuankeAPP:id/dialog_btn_left",
                                      retry_count=0,
                                      is_ignore_except_case=True, click_mode="click") is not None:
                utils_logger.log("检测到版本升级")
                return True
        elif self.query_ele_wrapper(
                self.get_query_str_within_xpath_only_text(text='哦耶，继续赚钱',
                                                          view_type='android.widget.Button'),
                is_ignore_except_case=True, retry_count=0, click_mode='click') is not None:
            utils_logger.log("检测到上次的试玩奖励")
            return True
        return False


class TaskAppiumZhuankeSign(TaskAppiumZhuankeBase):
    def __init__(self):
        TaskAppiumZhuankeBase.__init__(self)

    def run_task(self):
        if TaskAppiumZhuankeBase.run_task(self) is False:
            return False
        # 首页点击"每日抽奖"入口，进入抽奖界面
        # "每日抽奖"还有个空格，因此基于xpath
        if self.query_ele_wrapper(query_str="//android.view.View[contains(@content-desc, '每日抽奖')]",
                                  click_mode="click") is not None \
                or self.query_only_point_within_text('^每日抽奖$', is_auto_click=True) is not None:
            utils_logger.log("进入\"每日抽奖\"页面")
        else:
            self.task_scheduler_failed(message="not found \'每日抽奖\'")
            return False

        # 用于检测是否有抽奖机会
        if self.query_only_point_within_text(search_text='^您有0次抽奖机会$') is not None:
            return True

        # 点击抽奖
        if self.query_only_point_within_text(search_text='^点击$', is_auto_click=True) is not None \
                or self.query_ele_wrapper(query_str=self.get_query_str_by_viewid('lottery_btn'),
                                          click_mode="click") is not None:
            if self.query_point_size_within_text('^已发放到赚客账户$') > 0:
                return True
            # 虽然点击，但是不修改任务执行成功标识，等待下次再修改标识
            elif self.query_point_size_within_text('^您已多日未参与试玩任务$') > 0:
                self.task_scheduler_failed("找到\'您已多日未参与试玩任务\',请手动完成试玩任务")
                return False
            else:
                self.task_scheduler_failed('why zhuanke failed')
                return False
        else:
            self.task_scheduler_failed('未找到相关的抽奖按钮')
            return False
        return False

        # 查询抽奖状态，zhuanke_has_sign_once表示第一次已经签到成功
        if self.query_ele_wrapper(self.get_query_str_by_desc('分享获得更多抽奖机会')) is not None \
                or self.query_only_point_within_text('恭喜抽中现金奖励') is not None \
                or self.query_only_point_within_text('前往收徒任务分享') is not None:
            return True
        else:
            if self.query_only_point_within_text('前往试玩任务') is None:
                # 若没搜索到试玩任务请求，则直接退出
                self.task_scheduler_failed("抽奖失败")
            return False


class TaskAppiumZhuankeTrial(TaskAppiumZhuankeBase):
    """
    试玩逻辑
    """

    def __init__(self):
        TaskAppiumZhuankeBase.__init__(self)
        # 管理试玩任务新增的apk资源
        self.file_installed_pkg = envs.get_out_dir() + "/new_installed.txt"
        if os.path.exists(self.file_installed_pkg) is False:
            file = open(self.file_installed_pkg, 'w')
            file.close()
        else:
            for line in open(self.file_installed_pkg):
                utils_logger.log("start to uninstall apk:", line)
                utils_common.exec_shell_cmd('adb uninstall ' + line)

    def except_case_in_query_ele(self):
        if TaskAppiumZhuankeBase.except_case_in_query_ele(self) is True:
            return True
        if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('删除安装包'),
                                  is_ignore_except_case=True,
                                  retry_count=0) is not None:
            if self.query_ele_wrapper(
                    self.get_query_str_within_xpath_only_text('删除',
                                                              view_type='android.widget.Button'),
                    click_mode='click', is_ignore_except_case=True, retry_count=0) is not None:
                utils_logger.log("删除安装包")
                return True
        return False

    def query_installed_packages(self):
        "查询已安装应用列表"
        # 使用splitlines以行模式切割字符串
        installed_response, installed_response_error = utils_common.exec_shell_cmd(
            "adb shell pm list packages | awk -F ':' '{print $2}'").splitlines()
        return installed_response

    def run_task(self):
        return True
        # if TaskAppiumZhuankeBase.run_task(self) is False:
        #     return False
        # if self.query_only_point_within_text('试玩任务',is_auto_click=True,is_output_event_tract=True) is None:
        #     utils_logger.log("进入'试玩任务'失败"
        #     self.task_scheduler_failed("进入'试玩任务'失败")
        #     return False
        # if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('试玩'),click_mode='click') is None:
        #     self.task_scheduler_failed("选择'试玩'tab失败")
        #     return False
        # if self.wait_activity(driver=self.driver,target=['com.fc.zhuanke.ui.TaskListActivity']) is False:
        #     self.task_scheduler_failed('why not in 领取任务列表界面')
        #     return False
        # # 选择任务：不使用容器组件，使用任务的具体名称
        # # 以下为集中任务状态类别，其中剩余100份类似的表示可以点击
        # # //  cn.zhuanke.zhuankeAPP:id/NowzeroAmount      份数补充中   android.widget.TextView
        # # cn.zhuanke.zhuankeAPP:id/grabAmount 剩100份       android.widget.TextView
        # xpath_str="//android.widget.TextView[@resource-id='cn.zhuanke.zhuankeAPP:id/grabAmount']"
        # elements=self.driver.find_elements_by_xpath(xpath_str)
        # if len(elements) <=0:
        #     utils_logger.log("试玩任务已抢光，退出"
        #     return True
        # 
        # click_index=int(random.randint(0,len(elements)-1))
        # utils_logger.log("当前共有任务数量：",len(elements),",index:",click_index,",选中元素坐标：",elements[click_index].location
        # elements[click_index].click()
        # if self.wait_activity(self.driver,target=['com.fc.zhuanke.ui.PlayTaskDetailActivity'],is_ignore_except_case=True) is False:
        #     # 检测是否有未完成的任务
        #     if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(text='去完成',view_type='android.widget.Button'),click_mode='click',retry_count=0,is_ignore_except_case=True) is not None:
        #         utils_logger.log("有任务未完成"
        #     else:
        #         utils_logger.log("未进入任务详情界面，检查是否有未完成的任务失败"
        #         self.task_scheduler_failed('检查是否有未完成的任务失败')
        #         return False
        #         
        # # 校验'安装' - 应用安装逻辑
        # if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('已安装')) is None:
        #     # 若判断试玩应用还未安装，则先执行安装程序
        #     old_installed_packages=self.query_installed_packages()
        #     # 状态置为安装应用起始页面
        #     is_download_caught_exception=False  # 下载是否碰到异常
        #     for try_index in range(20):
        #         utils_logger.log("检查任务详情页状态：",try_index
        #         if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('下载'),click_mode='click',is_ignore_except_case=True,retry_count=0) is not None:
        #             utils_logger.log("开始下载：",try_index
        #             time.sleep(2)
        #         elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('下载中',is_force_match=False),is_ignore_except_case=True,retry_count=0) is not None:
        #             utils_logger.log("等待apk下载完成...:",try_index
        #             time.sleep(2)
        #         elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('安装'),click_mode='click',is_ignore_except_case=True,retry_count=0) is not None:
        #             utils_logger.log("开始安装"
        #         # 检查是否是安装应用界面或者是正在安装界面(包含安装完成后的去人页面，是'.InstallAppProgress')
        #         elif self.wait_activity(driver=self.driver,target=['.PackageInstallerActivity','.InstallAppProgress'],is_ignore_except_case=True,retry_count=0) is True:
        #             utils_logger.log("弹出安装应用界面"
        #             break
        #         # 检查下载状态是否失败,若失败则退出至任务列表重新选择任务
        #         elif self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('任务下载失败'),is_ignore_except_case=True,retry_count=0) is not None:
        #             utils_logger.log("任务下载失败"
        #             if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text(text='好的',view_type='android.widget.Button'),click_mode='click') is not None:
        #                 if self.query_ele_wrapper("//android.widget.TextView[@text='放弃' and @resource-id='cn.zhuanke.zhuankeAPP:id/backTv']",click_mode='click') is not None:
        #                     # 来自弹框中的'放弃'按钮
        #                     if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('放弃',view_type='android.widget.Button'),click_mode='click') is not None:
        #                         utils_logger.log("放弃该任务"
        #                     else:
        #                         self.task_scheduler_failed("'---> 放弃任务'失败")
        #                 else:
        #                     self.task_scheduler_failed("--->未找到左上角的返回按钮，即'放弃'")
        #             else:
        #                 self.task_scheduler_failed("---> 关闭'下载任务'弹框失败")
        #             is_download_caught_exception=True
        #             break
        #     if is_download_caught_exception is True:
        #         utils_logger.log("任务下载失败，放弃该任务,等待下次重新获取任务"
        #         return False
        #     # 执行安装流程并检测安装状态
        #     is_installed_success=False
        #     for check_if_installing_index in range(20):
        #         utils_logger.log("check_if_installing_index with index:",check_if_installing_index
        #         # 触发开始安装
        #         if self.wait_activity(self.driver,target=['.PackageInstallerActivity']) is True:
        #             utils_logger.log("此刻正在应用安装起始页面，触发安装开始逻辑"
        #             if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('通过华为应用市场安全检测。')) is not None:
        #                 if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('安装',view_type='android.widget.Button'),click_mode='click') is not None:
        #                     utils_logger.log("触发'通过华为应用市场监测'的安装流程"
        #                 else:
        #                     self.task_scheduler_failed("触发'通过华为应用市场监测'的安装流程'失败")
        #             else:
        #                 if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('我已充分了解该风险',is_force_match=False,view_type='android.widget.CheckBox'),click_mode='click') is not None:
        #                     utils_logger.log("触发'了解风险'按钮"
        #                 if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('继续安装',view_type='android.widget.Button'),click_mode='click') is not None:
        #                     utils_logger.log("触发'继续安装'弹框按钮"
        #         # 检查是否回到任务详情页
        #         elif self.wait_activity(self.driver,target=['com.fc.zhuanke.ui.PlayTaskDetailActivity'],is_ignore_except_case=True) is True:
        #             utils_logger.log("此刻认为应用已安装完成，退出系统应用安装界面"
        #             is_installed_success=True
        #             break
        #         # 识别到应用正在安装中，则等待
        #         elif self.wait_activity(self.driver,target=['.InstallAppProgress']) is True:
        #             xpath_install_done="//android.widget.Button[@text='完成' and @resource-id='com.android.packageinstaller:id/done_button']"
        #             if self.query_ele_wrapper(xpath_install_done,click_mode='click') is not None:
        #                 utils_logger.log("检测到'安装已完成'界面，触发'完成'按钮"
        #             else:
        #                 utils_logger.log("安装未完成,继续等待["+str(check_if_installing_index)+"]:",utils_appium.get_cur_act(self.driver)
        #                 time.sleep(3)
        #         else:
        #             self.task_scheduler_failed('not in 任何正确界面')
        #     if is_installed_success is False:
        #         utils_logger.log("应用安装失败"
        #         self.task_scheduler_failed('应用安装失败')
        #         return False
        #     # check 新安装的应用包名
        #     utils_logger.log("检测新安装的应用包名"
        #     for  new_installed_pkg_itme in self.query_installed_packages():
        #         if new_installed_pkg_itme not in old_installed_packages:
        #             utils_logger.log("检测到新的安装应用",new_installed_pkg_itme
        #             with open(self.file_installed_pkg, 'w') as f:
        #                 f.write(new_installed_pkg_itme)
        # # 计算休眠时间
        # wait_time_minutes=5 # 默认休眠5分钟
        # ele_txt=None
        # try:
        #     ele_txt=json.dumps(self.query_ele_wrapper(self.get_query_str_by_viewid('cn.zhuanke.zhuankeAPP:id/taskStep')).text, encoding='utf-8', ensure_ascii=False)
        #     ele_txt=str(ele_txt.replace('\"','').replace('\\',''))
        #     utils_logger.log("ele_txt:",ele_txt
        #     match_result=re.findall(r"试玩超过([0-9]\d*)分钟|体验超过([0-9]\d*)分钟|试玩([0-9]\d*)分钟", ele_txt)
        #     utils_logger.log("[match_result]",match_result
        #     for match_item in match_result:
        #         for item in match_item:
        #             if item == "":
        #                 continue
        #             wait_time_minutes=int(item)
        #             utils_logger.log("",wait_time_minutes
        # except:
        #     utils_logger.log(traceback.format_exc()
        #     self.task_scheduler_failed(ele_txt)
        # utils_logger.log("休眠等待安装分钟数:",wait_time_minutes
        # # 执行试用逻辑
        # if self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('已安装')) is not None \
        #     and self.query_ele_wrapper(self.get_query_str_within_xpath_only_text('试玩应用'),click_mode='click') is not None:
        #     utils_logger.log("休眠以等待试玩完成"
        #     time.sleep(wait_time_minutes*60)
        #     for line in open(self.file_installed_pkg):
        #         utils_logger.log("start to uninstall apk:",line
        #         utils_common.exec_shell_cmd('adb uninstall '+line)
        #     return True
        # else:
        #     self.task_scheduler_failed("未在赚客中检测到'安装'按钮")
        #     return False


if __name__ == "__main__":
    import inspect

    tasks = [left for left, right in inspect.getmembers(sys.modules[__name__], inspect.isclass)
             if not left.startswith('Basic')]
    while True:
        input_info = "------------------------执行任务列表-----------------------\n"
        for index, task_item in enumerate(tasks):
            input_info += str(index) + "：" + task_item + "\n"
        task_index_selected = input(input_info + "请选择需运行任务对应索引(索引下标越界触发程序退出)：")
        if task_index_selected.isdigit() is False:
            utils_logger.log("索引值非数字，请重新输入：", task_index_selected)
            continue
        task_index_selected = int(task_index_selected)
        if task_index_selected >= len(tasks) > 0:
            utils_logger.log("[" + str(task_index_selected) + "]任务索引不存在，退出程序...")
            break
        task_name = tasks[task_index_selected]
        task = eval(task_name + '()')
        task.run_task()
