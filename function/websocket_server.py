import asyncio
import websockets
import json
import os
import sys
from .message_handler import MessageHandler
from .heartbeat import HeartbeatMonitor
from .logger import get_logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

class WebSocketServer:
    def __init__(self, host: str = None, port: int = None, token: str = None):
        # 使用配置文件或默认值
        if HAS_CONFIG:
            self.host = host or config.WS_HOST
            self.port = port or config.WS_PORT
            self.token = token or config.WS_TOKEN
        else:
            self.host = host or "0.0.0.0"
            self.port = port or 9001
            self.token = token or "napcat_token_070421"
        
        self.message_handler = MessageHandler()
        self.heartbeat = HeartbeatMonitor()
        self.logger = get_logger()
    
    async def handler(self, websocket):
        """WebSocket连接处理器"""
        # 获取请求头
        auth = websocket.request.headers.get("Authorization")
        
        # 校验 token
        if auth != f"Bearer {self.token}":
            self.logger.warning(f"Token验证失败: {auth}")
            await websocket.close()
            return
        
        self.logger.info("NapCat WebSocket连接已建立")
        
        try:
            async for message in websocket:
                await self._process_message(websocket, message)
                
        except websockets.ConnectionClosed:
            self.logger.info("WebSocket连接已关闭")
        except Exception as e:
            self.logger.error(f"WebSocket处理异常: {e}")
    
    async def _process_message(self, websocket, message):
        """处理接收到的消息"""
        try:
            # 解析消息
            message_data = json.loads(message)
            self.logger.debug("收到原始消息", {"raw_message": message[:200]})

            # 处理消息，返回 (reply_text, action_data)
            reply_text, action_data = self.message_handler.handle_message(message_data)

            self.heartbeat.notify()

            if reply_text:
                reply = {
                    "action": "send_private_msg",
                    "params": {
                        "user_id": message_data.get("user_id"),
                        "message": reply_text,
                    },
                }
                await websocket.send(json.dumps(reply, ensure_ascii=False))
                self.logger.info(
                    f"发送私聊回复给用户 {message_data.get('user_id')}",
                    {"response": reply_text[:100]},
                )

            # 发送 action（如通过好友申请）
            if action_data:
                await websocket.send(json.dumps(action_data, ensure_ascii=False))
                self.logger.info(
                    f"发送 action: {action_data.get('action')}",
                    {"params": action_data.get("params")},
                )

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析错误: {e}", {"raw_message": message[:200]})
        except Exception as e:
            self.logger.error(f"处理消息时出错: {e}")
    
    async def start(self):
        """启动WebSocket服务器"""
        self.logger.info(f"启动WebSocket服务器，监听 {self.host}:{self.port}")
        
        server = await websockets.serve(
            self.handler,
            self.host,
            self.port
        )
        
        self.logger.info(f"服务器已启动，监听 {self.host}:{self.port}")
        self.logger.info(f"Token: {self.token}")
        
        # 显示统计信息
        stats = self.message_handler.get_statistics_summary()
        self.logger.info("服务器启动统计信息", stats)

        await self.heartbeat.start()
        
        await server.wait_closed()
    
    def run(self):
        """运行服务器"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            self.logger.info("收到键盘中断信号，正在关闭服务器...")
        except Exception as e:
            self.logger.error(f"服务器运行异常: {e}")
        finally:
            asyncio.run(self.heartbeat.stop())
            self.logger.info("服务器已停止")