from email.message import EmailMessage
from email.mime.text import MIMEText
import logging
from typing import Dict, List, Literal, Union
from ..core.interfaces.message_builder import IMessageBuilder


class MessageBuilder(IMessageBuilder):

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger


    def build_message(self, from_addr: str, to: Union[str, List[str]], body: Union[str, Dict[Literal['plain', 'csv', 'html', 'rtf'], str]], subject: Union[str, None] = None) -> EmailMessage:
        """
        Create an email message from parts
        :param to: the recipient email addresses of the message. Can be a string or a list of strings
        :param body: the content of the email. If it is a string, will be processed as plain text. If dictionary, will be interpreted as {type: content}, allowing other types of text content to be sent.
        :param subject: the subject of the email. Can be left empty
        :param file: a file attachment for the email. Can be of various types
        """

        message = EmailMessage()
        message['to'] = (',').join(to) if type(to) == List else to
        message['from'] = from_addr
        message['subject'] = subject

        # attach text to mail
        self._attach_body_to_message(message, body)

        return message
    

    def _attach_body_to_message(self, message: EmailMessage, body: Union[str, Dict[Literal['plain', 'csv', 'html', 'rtf'], str]]) -> EmailMessage:
        """
        attach given body content to given email message object
        """
        self.logger.debug(f"attaching to message: {body}")
        if type(body) == str:
            self.logger.debug(f"body is plain text. attaching...")

            message.set_content(body)

            return message
        
        for idx, (ctype, content) in enumerate(body.items()):
            message_content = MIMEText(content, ctype)

            if not idx:
                self.logger.debug(f"attaching to message: {message_content}")
                message.add_alternative(message_content)
            else:
                self.logger.debug(f"attaching alternative content: {message_content}")
                message.set_content(message_content)

        return message