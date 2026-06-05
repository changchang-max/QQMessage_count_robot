import smtplib
from email.mime.text import MIMEText
from .logger import get_logger

logger = get_logger()


def send_email(
    sender: str | None = None,
    passcode: str | None = None,
    receiver: str | None = None,
    subject: str | None = None,
    content: str | None = None,
    **kwargs,
) -> bool:
    if not content and "body" in kwargs:
        content = kwargs["body"]

    try:
        import config

        if not sender:
            sender = config.EMAIL_SENDER
        if not passcode:
            passcode = config.EMAIL_AUTH_CODE
        if not receiver:
            receiver = config.EMAIL_RECEIVER

        if not sender or not passcode or not receiver:
            msg = "邮箱配置不完整，请检查 environment.env"
            logger.error(msg)
            print(msg)
            return False

        message = MIMEText(content, "plain", "utf-8")
        message["From"] = sender
        message["To"] = receiver
        message["Subject"] = subject

        smtp_ssl = smtplib.SMTP_SSL("smtp.qq.com", 465)
        smtp_ssl.login(sender, passcode)
        smtp_ssl.send_message(message)
        smtp_ssl.quit()

        msg = f"To:{receiver} 邮件发送成功"
        logger.info(msg)
        print(msg)
        return True

    except smtplib.SMTPAuthenticationError:
        msg = "邮箱登录失败，请检查 QQ_EMAIL_AUTH_CODE 是否正确"
        logger.error(msg)
        print(msg)
    except smtplib.SMTPException as e:
        msg = f"SMTP 发送失败: {e}"
        logger.error(msg)
        print(msg)
    except Exception as e:
        msg = f"发送邮件时发生未知错误: {e}"
        logger.error(msg)
        print(msg)
    return False
