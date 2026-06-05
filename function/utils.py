import json
import os
from datetime import datetime
from typing import Dict, Any

from function.logger import get_logger

logger = get_logger()

def ensure_directory(directory: str):
    """确保目录存在"""
    os.makedirs(directory, exist_ok=True)

def save_json(data: Dict, file_path: str):
    """保存JSON数据到文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存JSON文件失败 {file_path}: {e}")
        logger.error(f"保存JSON文件失败 {file_path}: {e}")
        return False

def load_json(file_path: str) -> Dict:
    """从文件加载JSON数据"""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载JSON文件失败 {file_path}: {e}")
        logger.error(f"加载JSON文件失败 {file_path}: {e}")
        return {}

def timestamp_to_date(timestamp: int) -> str:
    """将时间戳转换为日期字符串 (YYYY-MM-DD)"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d")

def get_current_date() -> str:
    """获取当前日期字符串 (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")

def format_statistics(stats: Dict) -> str:
    """格式化统计信息为可读字符串"""
    lines = []
    for date, groups in stats.items():
        lines.append(f"{date}")
        for group_id, group_info in groups.items():
            group_name = group_info.get("group_name", f"群聊{group_id}")
            count = group_info.get("count", 0)
            lines.append(f"  {group_name}  消息数：{count}")
    return "\n".join(lines)

def validate_message_data(data: Dict[str, Any]) -> bool:
    """验证消息数据格式"""
    required_fields = ["message_type", "user_id"]
    
    for field in required_fields:
        if field not in data:
            print(f"消息缺少必要字段: {field}")
            logger.error(f"消息缺少必要字段: {field}")
            return False
    
    if data["message_type"] == "group" and "group_id" not in data:
        print("群聊消息缺少 group_id 字段")
        logger.error("群聊消息缺少 group_id 字段")
        return False
    
    return True