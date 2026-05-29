#!/bin/bash

echo "=================================================="
echo "QQ机器人启动脚本"
echo "=================================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
if ! python3 -c "import websockets" &> /dev/null; then
    echo "安装websockets依赖..."
    pip3 install websockets
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
    echo "依赖安装成功"
else
    echo "依赖已安装"
fi

echo ""
echo "=================================================="
echo "启动QQ机器人..."
echo "=================================================="
echo ""

# 运行主程序
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "机器人启动失败，请检查错误信息"
else
    echo ""
    echo "机器人已正常退出"
fi