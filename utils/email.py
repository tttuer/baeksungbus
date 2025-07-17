# email_utils.py
import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.settings import settings

EMAIL_USERNAME = settings.email_username
EMAIL_PASSWORD = settings.email_password
EMAIL_SERVER = settings.email_server
EMAIL_PORT = settings.email_port


async def send_email(to_email: str, subject: str, body: str):
    """
    지정된 이메일 주소로 이메일을 보냅니다.
    """
    if not all([EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_SERVER, EMAIL_PORT]):
        print(
            "Warning: Email server configuration is incomplete. Check your .env file."
        )
        # 실제 운영 환경에서는 예외를 발생시키거나 로그를 남기는 것이 좋습니다.
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"백성운수(주)"
        msg["To"] = to_email
        msg["Subject"] = subject

        part1 = MIMEText(body, "html")
        msg.attach(part1)

        # aiosmtplib 사용
        await aiosmtplib.send(
            msg,
            hostname=EMAIL_SERVER,
            port=EMAIL_PORT,
            username=EMAIL_USERNAME,
            password=EMAIL_PASSWORD,
            start_tls=True,  # Gmail은 STARTTLS를 사용 (587 포트)
        )
        return True
    except aiosmtplib.SMTPAuthenticationError:
        print("Error: Email authentication failed. Check username/password.")
        return False
    except aiosmtplib.SMTPConnectError:
        print(
            f"Error: SMTP server connection failed. Check server '{EMAIL_SERVER}' and port '{EMAIL_PORT}'."
        )
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
