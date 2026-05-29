@echo off
echo ==================================================
echo QQ机器人启动脚本
echo ==================================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖...
pip list | findstr websockets >nul
if errorlevel 1 (
    echo 安装websockets依赖...
    pip install websockets
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
    echo 依赖安装成功
) else (
    echo 依赖已安装
)

echo.
echo ==================================================
echo 启动QQ机器人...
echo ==================================================
echo.

REM 运行主程序
python main.py

if errorlevel 1 (
    echo.
    echo 机器人启动失败，请检查错误信息
    pause
) else (
    echo.
    echo 机器人已正常退出
)