"""
QQ机器人配置文件
敏感配置（如 WS_TOKEN）建议通过环境变量传入，或复制本文件为 config_local.py 填写后使用。
"""

import os

# WebSocket服务器配置
WS_HOST = "0.0.0.0"
WS_PORT = 9001
WS_TOKEN = os.environ.get("NAPCAT_TOKEN", "napcat_token_070421")

# 数据存储配置
MESSAGES_DIR = "messages"
CONFIGS_DIR = "configs"
FOLLOWS_FILE = "follows.txt"

# 保存间隔（秒）
SAVE_INTERVAL = 60

# 查询天数
QUERY_DAYS = 7

# 调试模式
DEBUG = True
