#!/bin/bash
# 
# 注意事项:
# 运行脚本需预先安装 homebrew (已经安装则需要更新到最新版本, 可能耗时较长, 可自行升级)
# 脚本参数(bash ./bootstrap.sh -ption)(无参数安装GUI依赖环境)
#   -c : 安装CLI依赖环境
#   -d : 安装GUI依赖环境
#   -h : 显示帮助信息 
#   -i : 初始化环境
# Appium 可安装 CLI or GUI 版本, 运行脚本不传参数时默认安装 GUI 依赖环境
# Appium(1.6.5) 依赖 Xcode8 + XCUITest(Xcode7及以下为UIAutomation)
# Appium 依赖 Xcode Command Line Tool ,执行 xcode-select --install 安装
# Appium server 端依赖 java 1.8 版本 ,需预先升级 java 环境
# XCUITest 依赖工具  ideviceinstaller (需要 /var/db/lockdown 目录的写权限 ,需执行 sudo chmod -R 777 /var/db/lockdown)
#                   carthage
#                   ios-deploy
#                   xcpretty
# 真机运行需要打开 Developler -> Enable UI Automation
# 执行完脚本后可以通过执行 appium-doctor --ios 检查环境是否配置成功
#
# 脚本分别安装以下依赖工具
#   1.node
#   2.cnpm (用于代替 npm 的国内镜像))
#   3.ideviceinstaller
#   4.carthage
#   5.ios-deploy
#   6.xcpretty
#   7.appium-doctor
#   8.app-inspector
#
# Auther : Zhangzuming
# Email  : zhangzuming1@yhd.com
set -e
# export PATH=$PATH:/usr/local/bin
BOLD="\033[1m"
PURPLE="\033[35m"
dependencies_list=("node" "cnpm" "carthage" "ideviceinstaller" "ios-deploy" "xcpretty" "appium-doctor" "app-inspector" "appium")
function show_helper() {
  echo "参数说明:"
  echo "-c 安装CLI依赖环境"
  echo "-d 安装GUI依赖环境"
  echo "-h 显示帮助信息 "
  echo "-i 初始化环境"
  echo "无参数默认执行 -d 命令"
  echo "Auther : Zhangzuming"
  echo "Email  : zhangzuming1@yhd.com"
}

function init_envir() {
  echo "Init environment ... ..."

  for item in ${dependencies_list[@]}; do
    if [[ ${item} = "node" || ${item} = "cnpm" ]]; then
      continue
    fi
    if command -v ${item} > /dev/null; then
      uninstall_dependence ${item}
    fi
    print_uninstall_proprogres ${item}
  done
  echo -e "\n${PURPLE}Completed !!!\033[0m"
  exit 1;
}

progress-bar() {
  local tips=${2}
  local per=${1}
  local elapsed=$(awk 'BEGIN{print '$per'*40 }')
  tips() {
    if [[ -n ${tips} ]]; then
      echo "$tips" | awk '{printf "%s %-25s",$1,$2}'
    fi
  }
  already_done() { 
    for ((done=0; done<elapsed; done=done+1)); do 
      printf "▇"; 
    done 
  }
  remaining() { 
    for ((remain=elapsed; remain<duration; remain=remain+1)); do 
      printf " "; 
    done 
  }
  percentage() { 
    local num=$(awk 'BEGIN{print '$per'*100 }')
    printf "| %s%%" $num; 
  }
  clean_line() { 
    printf "\r";
  }
  tips;
  already_done; 
  remaining; 
  percentage
  clean_line
}

function assert_has_brew() {
  if ! command -v brew > /dev/null; then
    echo "Please make sure that you have brew installed"
    exit 1
  else 
    read -p "It may take a long time to update homebrew ,would you want to update automatically [y/n]: " option
    # select option in "y" "n"
    # do   
    #   break  
    # done
    case "$option" in
    y ) brew update;;
    n ) exit 1;;
    * ) exit 1;;
    esac
  fi
}

function assert_has_dependence() {
  dep=${1}
  if ! command -v ${dep} > /dev/null; then
    return 0
  else 
    return 1
  fi
}

function install_cnpm() {
  echo "Install cpnm ... ..."
  if ! command -v cnpm > /dev/null; then
    npm install -g cnpm --registry=https://registry.npm.taobao.org
  else
    echo "cpnm has been installed "
  fi
}

function install_appium() {
  echo "Install appium ... ..."
  cnpm install -g appium@1.6.5
}

function install_ideviceinstaller() {
  echo "Install ideviceinstaller ... ..."
  brew install --HEASD ideviceinstaller
  # brew link --overwrite ideviceinstaller
}

function install_node() {
  echo "Install node ... ..."
  brew install node
}

function install_carthage() {
  echo "Install carthage ... ..."
  brew install carthage
}

function install_ios_deploy() {
  echo "Install ios-deploy ... ..."
  cnpm install -g ios-deploy
}

function install_xcpretty() {
  echo "Install xcpretty ... ..."
  sudo gem install -n /usr/local/bin xcpretty
}

function install_appium_doctor() {
  echo "Install appium-doctor ... ..."
  cnpm install -g appium-doctor
}

function install_app_inspector() {
  echo "Install app-inspector ... ..."
  cnpm install -g app-inspector
}

function install_macaca() {
  echo "Install macaca ... ..."
  cnpm install -g macaca-cli
}

function fetch_and_build_dependencies_gui_mode() {
  echo -e "${BOLD}Fetching dependencies(GUI_MODE)"

  assert_has_brew
  for item in ${dependencies_list[@]}; do
    if [[ ${item} = "appium" ]]; then
      continue
    fi
    if ! command -v ${item} > /dev/null; then
      echo "${item} is not installed"
      install_dependence ${item}
    else 
      echo "${item} has benn installed "
      continue
    fi
  done
  echo -e "${PURPLE}Completed !!!\033[0m"
}

function fetch_and_build_dependencies_cli_mode() {
  echo -e "${BOLD}Fetching dependencies(CLI_MODE)"

  assert_has_brew
  for item in ${dependencies_list[@]}; do
    if ! command -v ${item} > /dev/null; then
      echo "${item} is not installed"
      install_dependence ${item}
    else 
      echo "${item} has benn installed "
      continue
    fi
  done
  echo -e "${PURPLE}Completed !!!\033[0m"
}

function install_dependence() {
  option=${1}
  case "$option" in
    node             ) install_node;;
    cnpm             ) install_cnpm;;
    ideviceinstaller ) install_ideviceinstaller;;
    carthage         ) install_carthage;;
    ios-deploy       ) install_ios_deploy;;
    xcpretty         ) install_xcpretty;;
    appium-doctor    ) install_appium_doctor;;
    app-inspector    ) install_app_inspector;;
    appium           ) install_appium;;
    *                ) exit 1 ;;
  esac
}

function uninstall_dependence() {
  option=${1}
  case "$option" in
    carthage         ) brew uninstall carthage > /dev/null;;
    ideviceinstaller ) brew uninstall ideviceinstaller > /dev/null;;
    ios-deploy       ) cnpm uninstall ios-deploy > /dev/null;;
    xcpretty         ) gem uninstall xcpretty > /dev/null;;
    appium-doctor    ) cnpm uninstall -g appium-doctor > /dev/null;;
    app-inspector    ) cnpm uninstall -g app-inspector > /dev/null;;
    appium           ) cnpm uninstall -g appium > /dev/null;;
    *                ) exit 1 ;;
  esac
}

function print_uninstall_proprogres() {
  option=${1}
  case "$option" in
    carthage         ) progress-bar 0.2 "uninstall $option......";sleep 1;;
    ideviceinstaller ) progress-bar 0.4 "uninstall $option......";sleep 1;;
    ios-deploy       ) progress-bar 0.5 "uninstall $option......";sleep 1;;
    xcpretty         ) progress-bar 0.7 "uninstall $option......";sleep 1;;
    appium-doctor    ) progress-bar 0.8 "uninstall $option......";sleep 1;;
    app-inspector    ) progress-bar 0.9 "uninstall $option......";sleep 1;;
    appium           ) progress-bar 1 "uninstall $option......";sleep 1;;
    *                ) exit 1 ;;
  esac
}
while getopts " c d h i " option; do
  case "$option" in
    c ) FETCH_DEPS=1;;
    d ) FETCH_DEPS=2;;
    h ) show_helper; exit 1;;
    i ) init_envir; exit 1;;
    * ) exit 1 ;;
  esac
done

if [[ -n $FETCH_DEPS ]]; then
  case "$FETCH_DEPS" in
    1 ) fetch_and_build_dependencies_cli_mode;;
    2 ) fetch_and_build_dependencies_gui_mode;;
    * ) exit 1;;
  esac
fi
if [[ -z ${FETCH_DEPS} ]]; then 
  fetch_and_build_dependencies_gui_mode
fi