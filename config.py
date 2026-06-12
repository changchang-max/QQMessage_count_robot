"""
QQ机器人配置文件
敏感配置（如 WS_TOKEN）建议通过环境变量传入，或复制本文件为 config_local.py 填写后使用。
"""

import os
from dotenv import load_dotenv

# 加载 environment.env（如果存在）
load_dotenv("environment.env")

# WebSocket服务器配置
WS_HOST = "0.0.0.0"
WS_PORT = 9001
WS_TOKEN = os.environ.get("NAPCAT_TOKEN", "napcat_token_070421")

# 数据存储配置
MESSAGES_DIR = "data/messages"
CONFIGS_DIR = "data/configs"
FOLLOWS_FILE = "follows.txt"

# 保存间隔（秒）
SAVE_INTERVAL = 60

# 查询天数
QUERY_DAYS = 7

# 管理员QQ
ADMIN_QQ = os.environ.get("ADMIN_QQ", "")

# 调试模式
DEBUG = True

# 心跳监控配置
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "300"))
HEARTBEAT_REPLY_TIMEOUT = int(os.environ.get("HEARTBEAT_REPLY_TIMEOUT", "120"))
HEARTBEAT_GROUP_ID = int(os.environ.get("HEARTBEAT_GROUP_ID", "0"))
HEARTBEAT_TARGET_QQ = int(os.environ.get("HEARTBEAT_TARGET_QQ", "0"))
HEARTBEAT_SEND_MESSAGE = os.environ.get("HEARTBEAT_SEND_MESSAGE","心跳告警: 机器人超过5分钟未收到消息，请回复以确认正常运行。")

# QQ邮箱配置
EMAIL_SENDER = os.environ.get("QQ_EMAIL_SENDER", "")
EMAIL_RECEIVER = os.environ.get("QQ_EMAIL_RECEIVER", "")
EMAIL_AUTH_CODE = os.environ.get("QQ_EMAIL_AUTH_CODE", "")
