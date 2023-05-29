from pathlib import Path
import logging

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from_username),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Goit10 Corporation",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):

    """
    The send_email function sends an email to the user with a link that they can click on to verify their email address.

    :param email: EmailStr: Ensure that the email is a valid email address
    :param username: str: Pass the username of the user to be used in the email template
    :param host: str: Pass the hostname of the server to be used in the email template
    :return: A coroutine object

    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email!",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        logging.error(err)

