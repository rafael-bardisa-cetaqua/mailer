from abc import ABC, abstractmethod
from email.message import EmailMessage
from typing import Dict

class IFileAttacher(ABC):

    @abstractmethod
    def attach_files_to_message(self, filenames: Dict[str, str], message: EmailMessage) -> EmailMessage:
        """
        given pairs of file names, search for each file and attach it to the message under a new name
        """

    @abstractmethod
    def enable_sftp(self, host: str, user: str, password: str, sftp_pk_path: str, *, label: str="default") -> bool:
        """
        enable the use of an sftp server, given the server's information. Multiple can be stored specifying the label parameter
        :param host: the address of the sftp server to connect to
        :param user: the username to connect to the server
        :param password: the user's password in the sftp server
        :param sftp_pf_path: the path to a file containing the sftp server's public key
        :param label: which label to store the sftp connection as
        """

    @abstractmethod
    def disable_sftp(self, *, label: str="default") -> bool:
        ...
