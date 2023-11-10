from abc import ABC, abstractmethod
from email.message import EmailMessage
from typing import Dict, List, Literal, Union


class IMessageBuilder(ABC):

    @abstractmethod
    def build_message(self, from_addr: str, to: Union[str, List[str]], body: Union[str, Dict[Literal['plain', 'csv', 'html', 'rtf'], str]], subject: Union[str, None] = None) -> EmailMessage:
        """

        """