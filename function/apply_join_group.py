import json
from typing import Dict, Any, Optional, Tuple
from .logger import get_logger


class GroupInviteHandler:
    """处理群聊邀请，自动通过所有加群请求"""

    def __init__(self):
        self.logger = get_logger()

    def is_group_invite(self, message_data: Dict[str, Any]) -> bool:
        """判断是否为群聊邀请"""
        return (
            message_data.get("post_type") == "request"
            and message_data.get("request_type") == "group"
            and message_data.get("sub_type") == "invite"
        )

    def handle(self, message_data: Dict[str, Any]) -> Optional[Dict]:
        """
        处理群聊邀请。
        返回需要通过 WebSocket 发送的 action 数据，如果不是群邀请则返回 None。
        """
        if not self.is_group_invite(message_data):
            return None

        group_id = message_data.get("group_id")
        user_id = message_data.get("user_id")
        flag = message_data.get("flag")

        if not flag:
            self.logger.warning(
                f"收到群邀请但缺少 flag，无法处理",
                {"group_id": group_id, "user_id": user_id},
            )
            return None

        self.logger.info(
            f"收到群邀请，自动通过",
            {"group_id": group_id, "user_id": user_id, "flag": flag},
        )

        action = {
            "action": "set_group_add_request",
            "params": {
                "flag": flag,
                "sub_type": "invite",
                "approve": True,
            },
        }

        return action
