import json
from typing import Dict, Any, Optional, Tuple
from .logger import get_logger


class FriendRequestHandler:
    """处理加好友请求，自动通过所有好友申请"""

    def __init__(self):
        self.logger = get_logger()

    def is_friend_request(self, message_data: Dict[str, Any]) -> bool:
        """判断是否为加好友请求"""
        return (
            message_data.get("post_type") == "request"
            and message_data.get("request_type") == "friend"
        )

    def handle(self, message_data: Dict[str, Any]) -> Optional[Dict]:
        """
        处理加好友请求。
        返回需要通过 WebSocket 发送的 action 数据，如果不是好友请求则返回 None。
        """
        if not self.is_friend_request(message_data):
            return None

        user_id = message_data.get("user_id")
        flag = message_data.get("flag")
        comment = message_data.get("comment", "")

        if not flag:
            self.logger.warning(
                f"收到好友请求但缺少 flag，无法处理",
                {"user_id": user_id, "comment": comment},
            )
            return None

        self.logger.info(
            f"收到好友请求，自动通过",
            {"user_id": user_id, "flag": flag, "comment": comment},
        )

        # 构造通过好友申请的 action
        action = {
            "action": "set_friend_add_request",
            "params": {
                "flag": flag,
                "approve": True,
            },
        }

        return action
