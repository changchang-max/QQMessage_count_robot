import json
import os
from datetime import datetime, timedelta
import asyncio
import threading
import time
from typing import Dict, Any, Optional, Tuple
from .logger import get_logger
from .apply_add_friend import FriendRequestHandler

class MessageHandler:
    def __init__(self):
        self.messages_dir = "messages"
        self.configs_dir = "configs"
        self.follows_file = os.path.join(self.configs_dir, "follows.txt")
        self.save_interval = 60  # 保存间隔（秒）
        self._data_cache = {}  # 内存缓存，减少磁盘IO
        self._last_save_time = datetime.now()
        self.logger = get_logger()
        
        # 确保目录存在
        os.makedirs(self.messages_dir, exist_ok=True)
        os.makedirs(self.configs_dir, exist_ok=True)
        
        # 加载关注列表
        self.follows = self._load_follows()
        
        # 启动定时保存线程
        self._save_thread = threading.Thread(target=self._periodic_save_thread, daemon=True)
        self._save_thread.start()
        
        self.logger.info("消息处理器初始化完成", {
            "messages_dir": self.messages_dir,
            "configs_dir": self.configs_dir,
            "follows_count": len(self.follows)
        })
        
        self.friend_request_handler = FriendRequestHandler()
    
    def _load_follows(self) -> set:
        """加载关注列表"""
        follows = set()
        if os.path.exists(self.follows_file):
            try:
                with open(self.follows_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            follows.add(line)
                self.logger.info(f"加载关注列表成功，共 {len(follows)} 个用户")
            except Exception as e:
                self.logger.error(f"加载关注列表失败: {e}")
        else:
            self.logger.info("关注列表文件不存在，将创建新文件")
        return follows
    
    def _save_follows(self):
        """保存关注列表"""
        try:
            with open(self.follows_file, 'w', encoding='utf-8') as f:
                for qq in self.follows:
                    f.write(f"{qq}\n")
            self.logger.info(f"保存关注列表成功，共 {len(self.follows)} 个用户")
        except Exception as e:
            self.logger.error(f"保存关注列表失败: {e}")
    
    def _get_user_file_path(self, user_id: str) -> str:
        """获取用户数据文件路径"""
        return os.path.join(self.messages_dir, f"{user_id}.json")
    
    def _load_user_data(self, user_id: str) -> Dict:
        """加载用户数据（优先从缓存加载）"""
        # 首先检查缓存
        if user_id in self._data_cache:
            return self._data_cache[user_id].copy()  # 返回副本，避免修改原始数据
        
        # 缓存中没有，从文件加载
        file_path = self._get_user_file_path(user_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载用户 {user_id} 数据失败: {e}")
        return {}
    
    def _save_user_data(self, user_id: str, data: Dict):
        """保存用户数据到缓存，定时写入磁盘"""
        # 直接保存数据到缓存
        self._data_cache[user_id] = data
        
        # 记录调试信息
        if user_id in data and isinstance(data, dict):
            date_keys = list(data.keys())
            if date_keys:
                latest_date = date_keys[-1]
                if latest_date in data and isinstance(data[latest_date], dict):
                    group_count = len(data[latest_date])
                    self.logger.debug(f"用户 {user_id} 数据已缓存，最新日期 {latest_date}，群组数 {group_count}")
    
    def _periodic_save_thread(self):
        """定时保存数据到磁盘（线程版本）"""
        while True:
            time.sleep(self.save_interval)
            self._flush_cache_to_disk()
    
    def _flush_cache_to_disk(self):
        """将缓存数据写入磁盘"""
        if not self._data_cache:
            return
        
        try:
            for user_id, data in self._data_cache.items():
                file_path = self._get_user_file_path(user_id)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"已保存 {len(self._data_cache)} 个用户的数据到磁盘", {
                "user_count": len(self._data_cache),
                "users": list(self._data_cache.keys())
            })
            self._data_cache.clear()
        except Exception as e:
            self.logger.error(f"保存数据到磁盘失败: {e}")
    
    def _get_date_str(self, timestamp: int) -> str:
        """将时间戳转换为日期字符串"""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d")
    
    def handle_message(self, message_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict]]:
        """
        处理接收到的消息。
        返回 (reply_text, action_data)：
          - reply_text: 需要发送的私聊文本，无则为 None
          - action_data: 需要直接发送的 WebSocket action，无则为 None
        """
        try:
            # 记录消息日志
            self.logger.log_message(message_data)

            post_type = message_data.get("post_type")
            message_type = message_data.get("message_type")

            # 好友请求
            if post_type == "request":
                action = self.friend_request_handler.handle(message_data)
                return None, action

            # 普通消息
            if message_type == "group":
                return self._handle_group_message(message_data), None
            elif message_type == "private":
                return self._handle_private_message(message_data), None
            else:
                self.logger.warning(f"未知消息类型: post_type={post_type}, message_type={message_type}")
                return None, None

        except Exception as e:
            self.logger.error(f"处理消息时出错: {e}")
            return None, None
    
    def _handle_group_message(self, message_data: Dict[str, Any]) -> Optional[str]:
        """处理群聊消息"""
        user_id = str(message_data.get("user_id"))
        group_id = str(message_data.get("group_id"))
        group_name = message_data.get("group_name", f"群聊{group_id}")
        timestamp = message_data.get("time", int(datetime.now().timestamp()))
        
        # 检查是否在关注列表中
        if user_id not in self.follows:
            self.logger.debug(f"用户 {user_id} 不在关注列表中，忽略群聊消息")
            return None
        
        # 记录消息数量
        date_str = self._get_date_str(timestamp)
        
        # 加载用户数据
        user_data = self._load_user_data(user_id)
        
        # 初始化数据结构
        if date_str not in user_data:
            user_data[date_str] = {}
        
        if group_id not in user_data[date_str]:
            user_data[date_str][group_id] = {
                "group_name": group_name,
                "count": 0
            }
        
        # 增加消息计数
        user_data[date_str][group_id]["count"] += 1
        
        # 保存到缓存
        self._save_user_data(user_id, user_data)
        
        self.logger.info(f"记录群聊消息: 用户 {user_id} 在群 {group_name}({group_id}) 发送了消息", {
            "user_id": user_id,
            "group_id": group_id,
            "group_name": group_name,
            "date": date_str,
            "current_count": user_data[date_str][group_id]["count"]
        })
        return None
    
    def _handle_private_message(self, message_data: Dict[str, Any]) -> Optional[str]:
        """处理私聊消息"""
        user_id = str(message_data.get("user_id"))
        message = message_data.get("message", "").strip()
        
        # 处理指令
        if message == "/register":
            result = self._handle_register(user_id)
            self.logger.log_command("/register", user_id, result)
            return result
        elif message == "/select":
            result = self._handle_select(user_id)
            self.logger.log_command("/select", user_id, result[:100] if result else "无数据")
            return result
        elif message == "/help":
            result = self._handle_help()
            self.logger.log_command("/help", user_id, "显示帮助信息")
            return result
        else:
            self.logger.info(f"收到非指令私聊消息: {user_id}: {message}")
            # 非指令消息，提示可用指令
            result = self._handle_help()
            self.logger.log_command("非指令消息", user_id, "提示可用指令")
            return result
    
    def _handle_register(self, user_id: str) -> str:
        """处理关注指令"""
        if user_id in self.follows:
            self.logger.info(f"用户 {user_id} 已在关注列表中")
            return "您已经在关注列表中！"
        
        self.follows.add(user_id)
        self._save_follows()
        self.logger.info(f"用户 {user_id} 关注成功")
        return "关注成功！"
    
    def _handle_select(self, user_id: str) -> str:
        """处理查询指令"""
        user_data = self._load_user_data(user_id)
        
        if not user_data:
            return "您还没有任何聊天记录。"
        
        # 获取最近7天的日期
        today = datetime.now()
        recent_dates = []
        for i in range(7):
            date = today - timedelta(days=i)
            recent_dates.append(date.strftime("%Y-%m-%d"))
        
        # 构建回复消息
        response_lines = []
        for date_str in recent_dates:
            if date_str in user_data:
                date_data = user_data[date_str]
                if date_data:
                    response_lines.append(f"{date_str}")
                    for group_id, group_info in date_data.items():
                        group_name = group_info.get("group_name", f"群聊{group_id}")
                        count = group_info.get("count", 0)
                        response_lines.append(f"  {group_name}  消息数：{count}")
        
        if not response_lines:
            return "最近7天没有聊天记录。"
        
        return "\n".join(response_lines)
    
    def _handle_help(self) -> str:
        """处理帮助指令，显示所有可用指令"""
        help_text = """可用指令：

/register - 关注当前用户，开始统计您的群聊消息
/select   - 查询您最近7天在各群聊的消息数量
/help     - 显示此帮助信息

说明：
1. 发送 /register 后，机器人会开始统计您在群聊中的消息
2. 发送 /select 可以查看您的消息统计
3. 统计每分钟自动保存一次"""
        return help_text
    
    def get_statistics_summary(self) -> Dict:
        """获取统计摘要"""
        summary = {
            "total_follows": len(self.follows),
            "cached_users": len(self._data_cache),
            "last_save": self._last_save_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return summary