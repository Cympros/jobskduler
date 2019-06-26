#!/usr/bin/env bash

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

#echo "\n"

# 先暂存当前执行脚本的路径，方便后面cd
baseDirForScriptSelf=$(cd "$(dirname "$0")"; pwd)
cd ${baseDirForScriptSelf}

# git密码保存，免于下次git操作重复输入账号&密码
git config --global credential.helper store

# 参考文档:https://stackoverflow.com/questions/5626960/python-print-statement-with-utf-8-and-nohup
export PYTHONIOENCODING=utf-8

echo -e "确认使用以下python环境吗(yes or no)?  ["`which python`"]"
read use_pathon_path
if [[ ${use_pathon_path} == "yes" ]]; then
    # 安装python依赖环境
    echo "### 开始安装python依赖包"
    # 以下方案可屏蔽部分库下载失败引发后续依赖库库下载失败得情况
    cat ${baseDirForScriptSelf}/requirements.txt | xargs -n 1 pip install
fi

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
elif [[ "$(expr substr $(uname -s) 1 10)"=="MINGW32_NT" ]];then
    echo '---> Environment with Windows'
    exit
fi

# 解决npm安装速度太慢:使用cnpm
sudo npm install -g cnpm --registry=https://registry.npm.taobao.org
#安装appium：指定appium版本，经过验证可使用,使用'appium -v'验证版本
install_if_not_exist "appium" "sudo cnpm install -g appium@1.8.1"
## 调用'appium-doctor --android'检查appium环境
sudo cnpm install appium-doctor -g
# 安装uiautomator2
sudo cnpm install appium-uiautomator2-driver

# 开始检测appium-android依赖环境
appium-doctor --android