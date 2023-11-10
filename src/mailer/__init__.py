import logging
from smtplib import SMTP_PORT
from typing import Dict, List, Literal, Union

from .src.core.types import MailerConfig

from .src.message_builder.message_builder import MessageBuilder
from .src.file_attacher.file_attacher import FileAttacher

from .src.core.interfaces.mailer_interface import IMailer
from .src.core.mailer import Mailer

__version__ = "0.1.0"

# TODO reexport mailer with default build and signature
"""
def __init__(self, sender_addr: str, sender_pass: str, smtp_server_addr: str = 'smtp.gmail.com', smtp_server_port: int = SMTP_PORT, logger: logging.Logger = logger) -> None:
"""

class EmailAPI(IMailer):
    """
    Simple abstraction class for sending emails using smtp. Designed to be used as a git submodule, more info in the README page
    """

    def __init__(self, sender_addr: str, sender_pass: str, smtp_server_addr: str = 'smtp.gmail.com', smtp_server_port: int = SMTP_PORT, logger: logging.Logger = logging.Logger(__name__)) -> None:
        message_builder = MessageBuilder(logger)
        file_attacher = FileAttacher(logger)

        config: MailerConfig = {"sender_addr": sender_addr,
                                "sender_pass": sender_pass,
                                "smtp_server_addr": smtp_server_addr,
                                "smtp_server_port": smtp_server_port}
        
        self.mailer = Mailer(file_attacher, message_builder, config, logger)


    def send_email(self, to: Union[str, List[str]], body: Union[str, Dict[Literal['plain', 'csv', 'html', 'rtf'], str]], subject: Union[str, None] = None, attachments: Union[Dict[str, str], List[str]] = []) -> bool:
        return self.mailer.send_email(to, body, subject, attachments)


    def enable_sftp(self, host: str, user: str, password: str, sftp_pk_path: str, *, label: str="default") -> bool:
        return self.mailer.enable_sftp(host, user, password, sftp_pk_path, label=label)