import asyncio
from enum import Enum
from typing import Callable, Optional
from .logger import get_logger

logger = get_logger()


class HeartbeatState(Enum):
    MONITORING = "MONITORING"
    ALERTING = "ALERTING"


class HeartbeatMonitor:
    def __init__(self, interval: Optional[int] = None, reply_timeout: Optional[int] = None):
        try:
            import config
            self._interval = interval or getattr(config, "HEARTBEAT_INTERVAL", 300)
            self._reply_timeout = reply_timeout or getattr(config, "HEARTBEAT_REPLY_TIMEOUT", 120)
        except (ImportError, AttributeError):
            self._interval = interval or 300
            self._reply_timeout = reply_timeout or 120

        self._state = HeartbeatState.MONITORING
        self._running = False
        self._task = None

        self.on_send_alert: Optional[Callable[[], Optional[tuple[int, int, str]]]] = None
        self.on_send_email: Optional[Callable[[], None]] = None

        self._alert_group_id = None
        self._alert_target_qq = None
        self._elapsed = 0

    @property
    def state(self) -> str:
        return self._state.value

    def notify(self):
        if self._state == HeartbeatState.MONITORING:
            self._elapsed = 0
            logger.info(f"心跳: 收到消息，重置静默计时器 [state={self._state.value}]")

    def notify_reply(self, group_id: int, user_id: int):
        if self._state == HeartbeatState.ALERTING:
            if group_id == self._alert_group_id and user_id == self._alert_target_qq:
                logger.info(f"心跳: 收到目标回复 群:{group_id} QQ:{user_id}，恢复 MONITORING")
                self._reset_to_monitoring()
            else:
                logger.info(f"心跳: 忽略非目标回复 群:{group_id} QQ:{user_id} [state={self._state.value}]")

    def _reset_to_monitoring(self):
        self._state = HeartbeatState.MONITORING
        self._elapsed = 0
        self._alert_group_id = None
        self._alert_target_qq = None

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._cycle())
        logger.info(f"心跳监控已启动 (interval={self._interval}s, reply_timeout={self._reply_timeout}s) state={self._state.value}")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("心跳监控已停止")

    async def _cycle(self):
        while self._running:
            await asyncio.sleep(1)
            self._elapsed += 1

            if self._state == HeartbeatState.MONITORING:
                if self._elapsed >= self._interval:
                    logger.warning(f"心跳: 静默 {self._interval}s，触发告警")
                    try:
                        alert_cb = self.on_send_alert
                        if alert_cb:
                            result = alert_cb()
                            if result and len(result) == 3:
                                self._alert_group_id, self._alert_target_qq, _ = result
                                self._state = HeartbeatState.ALERTING
                                self._elapsed = 0
                                logger.info(f"心跳: MONITORING -> ALERTING (等待回复 群:{self._alert_group_id} QQ:{self._alert_target_qq})")
                                continue
                    except Exception as e:
                        logger.error(f"心跳: on_send_alert 回调异常: {e}")
                    self._elapsed = 0

            elif self._state == HeartbeatState.ALERTING:
                if self._elapsed >= self._reply_timeout:
                    logger.warning(f"心跳: 回复超时 {self._reply_timeout}s")
                    try:
                        email_cb = self.on_send_email
                        if email_cb:
                            email_cb()
                    except Exception as e:
                        logger.error(f"心跳: on_send_email 回调异常: {e}")
                    self._reset_to_monitoring()
                    logger.info("心跳: ALERTING -> MONITORING (回复超时)")
