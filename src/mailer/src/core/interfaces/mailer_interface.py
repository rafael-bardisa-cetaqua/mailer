from abc import ABC, abstractmethod
from typing import Dict, List, Literal, Union

class IMailer(ABC):

    @abstractmethod
    def send_email(self, to: Union[str, List[str]], body: Union[str, Dict[Literal['plain', 'csv', 'html', 'rtf'], str]], subject: Union[str, None] = None, attachments: Union[Dict[str, str], List[str]] = []) -> bool:
        """
        Sends an email to specified addresses
        :param to: the recipient email addresses of the message. Can be a string or a list of strings
        :param body: the content of the email. If string, will be processed as plain text. If dictionary, will be interpreted as {type: content}, allowing other types of text content to be sent.
        :param subject: the subject of the email. Default is empty
        :param attachments: file attachments for the email. Can be either list of file paths or dict of {filepath: name_in_email}. Default is empty
        """

    @abstractmethod
    def enable_sftp(self, host: str, user: str, password: str, sftp_pk_path: str, *, label: str="default") -> bool:
        """
        Enables an sftp connection to retrieve remote attachments for emails.
        """
