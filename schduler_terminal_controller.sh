#!/usr/bin/env bash

# tips:"bash -n <scritp_name>"可以执行语法检查，其并不执行代码

# 根据区间产生随机数
function rand(){
    min=$1
    max=$(($2-$min+1))
    num=$(($RANDOM+1000000000)) #增加一个10位的数再求余
    echo $(($num%$max+$min))
}

# 检测命令是否安装
function check_command_existed(){
	if command -v $1 >/dev/null 2>&1;then
		return 1
	else
		return 0
	fi 
}

function install_if_not_exist(){
	check_cmd=$1
	operate=$2
	check_command_existed ${check_cmd}
	if [[ "$?" -eq 0 ]];then
		echo ${check_cmd}" not existed,run to install....."
		eval ${operate}
	#else
	#	echo ${check_cmd}" has installed"
	fi
}
function update_environment(){
    # 检查运行环境并安装未成功的依赖
    if [[ "$(uname)" == "Darwin" ]];then
        echo '---> Environment with Mac-OSX'
        install_if_not_exist 'brew' '/usr/bin/ruby -e \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)\"'
    elif [[ "$(expr substr $(uname -s) 1 5)"=="Linux" ]];then
        echo '---> Environment with Linux'
        install_if_not_exist "virtualenv" "sudo apt-get install virtualenv"
        install_if_not_exist "adb" "sudo apt-get install android-tools-adb"
        install_if_not_exist "aapt" "sudo apt-get install aapt"
        install_if_not_exist "pip" "sudo apt-get install python-pip"
    
        install_if_not_exist "node" "sudo apt-get install nodejs"
        install_if_not_exist "npm" "sudo apt-get install npm"
        # 配置虚拟环境
        echo "--------->use python env: "`which python`
    elif [[ "$(expr substr $(uname -s) 1 10)"=="MINGW32_NT" ]];then
        echo '---> Environment with Windows'
        exit
    fi
    
    # todo npm初次安装即可
    ## 解决npm安装速度太慢:使用cnpm
    #sudo npm install -g cnpm --registry=https://registry.npm.taobao.org
    ##安装appium：指定appium版本，经过验证可使用,使用'appium -v'验证版本
    #install_if_not_exist "appium" "sudo cnpm install -g appium@1.8.1"
    ## 调用'appium-doctor --android'检查appium环境
    #sudo cnpm install appium-doctor -g
    ## 安装uiautomator2
    #sudo cnpm install appium-uiautomator2-driver
}

# 先暂存当前执行脚本的路径，方便后面cd
baseDirForScriptSelf=$(cd "$(dirname "$0")"; pwd)
cd ${baseDirForScriptSelf}

# git密码保存，免于下次git操作重复输入账号&密码
git config --global credential.helper store

# 参考文档:https://stackoverflow.com/questions/5626960/python-print-statement-with-utf-8-and-nohup
export PYTHONIOENCODING=utf-8

# 根据用户输入判断执行模式
echo -e "输入接下来的任务编号:\n    (0):循环执行任务\n    (1):初始化或更新运行环境\n    (2)扩展任务\n接下来你的回答是(0/1/2)？"
read answer
if [[ ${answer} == "0" ]]; then
    # 判断是否有其他地方正在执行该任务，是则放弃该位置的执行操作
    is_whether_task_running=`ps -ef | grep "terminal_controller.py" | grep -v -E "grep|$$"`
    if [[ ${is_whether_task_running} == "" ]];then
        while true
        do
            # terminal_controller脚本中若检测到有代码更新则会退出，否则会一直阻塞
            python terminal_controller.py
            
            # kill掉job_terminal_controller.py进程
            ps -ef | grep "terminal_controller.py" | grep -v -E "grep|$$" | awk  '{print "kill -9 " $2}' | sh
            
            # 同步代码
            git push > /dev/null
            
            echo "重启任务中......."
        done
    else
        echo "其他位置正在执行任务，请确认....."
        kill_cmd="ps -ef | grep -E 'schduler_terminal_controller.sh|terminal_controller.py' | grep -v -E \"grep|$$\" "
        echo "强杀方案："${kill_cmd}" | awk  '{print \"kill -9 \" \$2}' | sh"
    fi
elif [[ ${answer} == "1" ]]; then
    echo "初始化或更新运行环境"
    update_environment
    # 根据requirements.txt安装依赖库,由于该文件所在路径限制，必须放在${baseDirForScriptSelf}下执行
    # 屏蔽部分库下载失败引发后续依赖库库下载失败
    cat requirements.txt | xargs -n 1 pip install
elif [[ ${answer} == "2" ]]; then
    python job/job_normal.py
else
    echo "don\`t known what you want to do..."
fi