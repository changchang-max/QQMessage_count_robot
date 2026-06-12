import os
import json
from datetime import datetime, timedelta
import threading
import time
import queue
from typing import Dict, Any, List
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AsyncLogger:
    def __init__(self, logs_dir: str = "data/logs", max_queue_size: int = 1000):
        self.logs_dir = logs_dir
        self.max_queue_size = max_queue_size
        self.log_queue = queue.Queue(maxsize=max_queue_size)
        self._current_date = None
        self._log_file = None
        self._log_buffer = []
        self._flush_interval = 60  # 秒
        self._running = True
        
        # 确保日志目录存在
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 启动日志写入线程
        self._write_thread = threading.Thread(target=self._write_logs_thread, daemon=True)
        self._write_thread.start()
        
        # 启动定时刷新线程
        self._flush_thread = threading.Thread(target=self._periodic_flush_thread, daemon=True)
        self._flush_thread.start()
        
        self.info("日志系统初始化完成")
    
    def _get_log_file_path(self) -> str:
        """获取当前日期的日志文件路径"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.logs_dir, f"{date_str}.log")
    
    def _ensure_log_file(self):
        """确保日志文件已打开"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        if self._current_date != current_date or self._log_file is None:
            # 关闭旧文件（如果存在）
            if self._log_file:
                self._log_file.close()
            
            # 打开新文件
            log_path = self._get_log_file_path()
            self._log_file = open(log_path, 'a', encoding='utf-8')
            self._current_date = current_date
    
    def _write_log_entry(self, level: LogLevel, message: str, extra: Dict = None):
        """写入日志条目"""
        try:
            self._ensure_log_file()
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level.value,
                "message": message
            }
            
            if extra:
                log_entry["extra"] = extra
            
            # 写入到缓冲区
            self._log_buffer.append(json.dumps(log_entry, ensure_ascii=False))
            
        except Exception as e:
            print(f"写入日志失败: {e}")
    
    def _flush_buffer(self):
        """将缓冲区内容写入文件"""
        if not self._log_buffer:
            return
        
        try:
            self._ensure_log_file()
            
            for entry in self._log_buffer:
                self._log_file.write(entry + "\n")
            
            self._log_file.flush()
            self._log_buffer.clear()
            
        except Exception as e:
            print(f"刷新日志缓冲区失败: {e}")
    
    def _write_logs_thread(self):
        """日志写入线程"""
        while self._running:
            try:
                # 从队列获取日志条目（最多等待1秒）
                try:
                    log_data = self.log_queue.get(timeout=1)
                    level, message, extra = log_data
                    self._write_log_entry(level, message, extra)
                    self.log_queue.task_done()
                except queue.Empty:
                    continue
                    
            except Exception as e:
                print(f"日志写入线程错误: {e}")
    
    def _periodic_flush_thread(self):
        """定时刷新线程"""
        while self._running:
            time.sleep(self._flush_interval)
            self._flush_buffer()
    
    def log(self, level: LogLevel, message: str, extra: Dict = None):
        """记录日志"""
        try:
            self.log_queue.put((level, message, extra), timeout=0.5)
        except queue.Full:
            print(f"日志队列已满，丢弃日志: {message}")
        except Exception as e:
            print(f"记录日志失败: {e}")
    
    def debug(self, message: str, extra: Dict = None):
        """记录调试日志"""
        self.log(LogLevel.DEBUG, message, extra)
    
    def info(self, message: str, extra: Dict = None):
        """记录信息日志"""
        self.log(LogLevel.INFO, message, extra)
    
    def warning(self, message: str, extra: Dict = None):
        """记录警告日志"""
        self.log(LogLevel.WARNING, message, extra)
    
    def error(self, message: str, extra: Dict = None):
        """记录错误日志"""
        self.log(LogLevel.ERROR, message, extra)
    
    def critical(self, message: str, extra: Dict = None):
        """记录严重错误日志"""
        self.log(LogLevel.CRITICAL, message, extra)
    
    def log_message(self, message_data: Dict[str, Any]):
        """记录消息日志"""
        try:
            message_type = message_data.get("message_type", "unknown")
            user_id = message_data.get("user_id", "unknown")
            group_id = message_data.get("group_id", "private")
            raw_message = message_data.get("raw_message", "")[:100]
            
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if message_type == "group":
                print(f"[{ts}] [群聊] 用户: {user_id} | 群: {group_id} | 内容: {raw_message}")
            elif message_type == "private":
                print(f"[{ts}] [私聊] 用户: {user_id} | 内容: {raw_message}")
            else:
                print(f"[{ts}] [{message_type}] 用户: {user_id} | 内容: {raw_message}")
            
            extra = {
                "message_type": message_type,
                "user_id": user_id,
                "group_id": group_id,
                "raw_message": raw_message
            }
            
            if message_type == "group":
                self.info(f"收到群聊消息: 用户 {user_id} 在群 {group_id}", extra)
            elif message_type == "private":
                message = message_data.get("message", "")
                if message.startswith("/"):
                    self.info(f"收到私聊指令: {message} (用户: {user_id})", extra)
                else:
                    self.info(f"收到私聊消息: {message} (用户: {user_id})", extra)
            else:
                self.info(f"收到未知类型消息: {message_type}", extra)
                
        except Exception as e:
            self.error(f"记录消息日志失败: {e}")
    
    def log_command(self, command: str, user_id: str, result: str):
        """记录指令执行日志"""
        extra = {
            "command": command,
            "user_id": user_id,
            "result": result[:200]  # 只记录前200字符
        }
        self.info(f"执行指令: {command} (用户: {user_id})", extra)
    
    def shutdown(self):
        """关闭日志系统"""
        self._running = False
        self._flush_buffer()
        
        if self._log_file:
            self._log_file.close()
            self._log_file = None
        
        self.info("日志系统已关闭")

# 全局日志实例
_logger_instance = None

def get_logger() -> AsyncLogger:
    """获取全局日志实例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AsyncLogger()
    return _logger_instance