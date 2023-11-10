from email.mime.text import MIMEText
from email.message import EmailMessage

from urllib.parse import urlparse

import mimetypes
import smtplib
from smtplib import SMTPServerDisconnected

import requests

from smtplib import SMTP_PORT

import logging
from typing import Dict, List, Literal, Union

from .types import MailerConfig
from .interfaces.mailer_interface import IMailer
from .interfaces.message_builder import IMessageBuilder
from .interfaces.file_attacher import IFileAttacher


# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('\033[95m[%(levelname)-s]\033[0m %(funcName)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

#TODO probar que funciona como el alarm system
class Mailer(IMailer):
    """
    Simple abstraction class for sending emails using smtp. Designed to be used as a git submodule, more info in the README page
    """
    sender_addr: str
    sender_pass: str
    smtp_server_addr: str
    smtp_server_port: int
    logger: logging.Logger

    sftp_on: bool = False

    def __init__(self, file_attacher: IFileAttacher, message_builder: IMessageBuilder, config: MailerConfig, logger: logging.Logger = logger) -> None:
        """
        Create an email sender class. Provides default values for gmail smtp server to be used
        :param sender_addr: Email address to use for sending emails.
        :param sender_pass: Password for the above email address to use.
        :param smtp_server_addr: Optional, Which smtp server to log in to use the email address. The default value allows to use gmail accounts.
        :param smtp_server_port: Optional, the port used to connect to the server. Defaults to the default SMTP_PORT
        :param logger: Optional, logger to follow the program flow. Default does not log
        """
        self.logger = logger

        self.file_attacher = file_attacher
        self.message_builder = message_builder

        self.smtp_server_addr = config['smtp_server_addr']
        self.smtp_server_port = config['smtp_server_port']

        if not config['sender_addr']:
            raise ValueError("Sender address cannot be empty")
        
        if not config['sender_pass']:
            raise ValueError("Sender password cannot be empty")

        self.sender_addr = config['sender_addr']
        self.sender_pass = config['sender_pass']

        self.logger.debug(f"Mailer instantiated: {self.sender_addr = }, self.sender_pass = {'*'*len(self.sender_pass)}, self.smtp_server_addr = {self.smtp_server_addr + ':' + str(self.smtp_server_port) if self.smtp_server_port else config['smtp_server_addr']}")


    def send_email(self, to: Union[str, List[str]], body: Union[str, Dict[Literal['plain', 'csv', 'html', 'rtf'], str]], subject: Union[str, None] = None, attachments: Union[Dict[str, str], List[str]] = []) -> bool:
        """
        Sends an email to specified addresses
        :param to: the recipient email addresses of the message. Can be a string or a list of strings
        :param body: the content of the email. If string, will be processed as plain text. If dictionary, will be interpreted as {type: content}, allowing other types of text content to be sent.
        :param subject: the subject of the email. Default is empty
        :param attachments: file attachments for the email. Can be either list of file paths or dict of {filepath: name_in_email}. Default is empty
        """
        s = smtplib.SMTP(self.smtp_server_addr, self.smtp_server_port)

        try:
            s.starttls()
            s.login(self.sender_addr, self.sender_pass)

            base_message = self.message_builder.build_message(from_addr=self.sender_addr, to=to, body=body, subject=subject)

            if type(attachments) == list:
                attachments = {file: file for file in attachments}

            full_message = self.file_attacher.attach_files_to_message(attachments, base_message)

            self.logger.debug(f"sending email to {to}:\n\033[94m{subject}\033[0m\n\n{body}\n\nAttachments: {attachments}")
            s.sendmail(self.sender_addr, to, full_message.as_string())
            self.logger.debug(full_message.get_body())
            s.quit()

            return True
        
        except Exception as e:
            self.logger.error(f"program caught exception: {e}")
            # TODO specify exceptions
            return False
    

# TODO crear enable sftp
    def enable_sftp(self, host: str, user: str, password: str, sftp_pk_path: str, *, label: str="default") -> bool:
        return self.file_attacher.enable_sftp(host, user, password, sftp_pk_path, label=label)


    def _is_valid_smtp_connection_settings(self) -> bool:
        """
        checks if self smtp settings can be used to create valid connection
        """

        try:
            s = smtplib.SMTP(self.smtp_server_addr, self.smtp_server_port)
            status = s.noop()[0]
            s.quit()

        except ConnectionRefusedError:
            status = -1

        finally:
            return True if status == 250 else False