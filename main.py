#!/usr/bin/env python3
"""
QQ机器人主程序
功能：
1. 接收NapCat WebSocket消息
2. 处理群聊消息统计（仅统计关注用户）
3. 处理私聊指令（/register, /select, /help）
4. 每分钟自动保存数据到磁盘
5. 异步日志记录，每天一个日志文件
"""

import sys
import os
import atexit

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from function.websocket_server import WebSocketServer
from function.logger import get_logger

def main():
    """主函数"""
    # 初始化日志
    logger = get_logger()
    logger.info("=" * 50)
    logger.info("QQ机器人启动中...")
    logger.info("=" * 50)
    
    # 注册退出时的清理函数
    def cleanup():
        logger.info("正在清理资源...")
        logger.shutdown()
    
    atexit.register(cleanup)
    
    # 创建并启动WebSocket服务器
    server = WebSocketServer()
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"服务器运行出错: {e}")
    finally:
        logger.info("QQ机器人已停止")

if __name__ == "__main__":
    main()