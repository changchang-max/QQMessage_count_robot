import asyncio
from .logger import get_logger
from .email_sender import send_email

logger = get_logger()

class HeartbeatMonitor:
    MAX_ALERTS = 3

    def __init__(self, interval: int = 300):
        self._interval = interval
        self._has_message = False
        self._alert_count = 0
        self._running = False
        self._task = None

    def notify(self):
        self._has_message = True
        if self._alert_count > 0:
            self._alert_count = 0
            logger.info("心跳: 收到消息，重置提醒次数")

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._cycle())
        logger.info(f"心跳监控已启动，检测周期 {self._interval} 秒")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("心跳监控已停止")

    async def _cycle(self):
        while self._running:
            await asyncio.sleep(self._interval)

            if self._has_message:
                logger.info("心跳: 本周期收到消息，跳过告警")
                self._has_message = False
            else:
                self._alert_count += 1
                if self._alert_count <= self.MAX_ALERTS:
                    logger.warning(f"心跳: 第 {self._alert_count}/{self.MAX_ALERTS} 次未收到消息，发送告警邮件")
                    send_email(
                        subject=f"QQ机器人心跳告警 (第{self._alert_count}次提醒)",
                        body=f"QQ 机器人已连续 {self._interval // 60} 分钟未收到任何消息，可能已掉线，请检查。\n\n这是第 {self._alert_count} 次提醒，共 {self.MAX_ALERTS} 次。"
                    )
                else:
                    logger.warning(f"心跳: 第 {self._alert_count} 次未收到消息，已超过最大提醒次数 ({self.MAX_ALERTS})，不再发送邮件")
