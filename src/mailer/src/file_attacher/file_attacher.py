from collections import defaultdict
from email.message import EmailMessage
import logging
import mimetypes
from typing import Any, Dict, Union
import pysftp

from pysftp.exceptions import ConnectionException, CredentialException, HostKeysException

import requests
from ..core.interfaces.file_attacher import IFileAttacher
from .types import SFTPOpts

class FileAttacher(IFileAttacher):
    sftp_opts: Dict[str, SFTPOpts]

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.sftp_opts = {}


    def attach_files_to_message(self, filenames: Dict[str, str], message: EmailMessage) -> EmailMessage:
        """
        attach the given list of files to the given message
        """
        self.logger.debug(f"attaching to message: {filenames}")

        for file, email_filename in filenames.items():
            # Attach file to email
            (content_type, encondig) = mimetypes.guess_type(file)

            if content_type is None or encondig is not None:
                content_type = 'application/octet-stream'

            (maintype, subtype) = content_type.split('/', 1)
            self.logger.debug(f"content of file inferred to be: {(content_type, subtype)}")

            content = self.resolve_file_contents(file)
            if not content:
                self.logger.warning(f"could not attach {file} to email")
                continue

            self.logger.debug(f"attaching {maintype}/{subtype} content as {email_filename}: {content[:30]}...")
            message.add_attachment(content, maintype, subtype, filename=email_filename)

        self.logger.debug(f"files attached to message")
        return message
    

    # TODO validate connection
    def enable_sftp(self, host: str, user: str, password: str, sftp_pk_path: str, *, label: str="default") -> bool:
        """
        sets the given sftp server to be the default source of attachments
        """
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys.load(sftp_pk_path)

        self.sftp_opts[label] = SFTPOpts(host=host, username=user, password=password, cnopts=cnopts)
        return True


    def disable_sftp(self, *, label: str="default") -> bool:
        del self.sftp_opts[label]
        return True

    
    def resolve_file_contents(self, filename: str) -> bytes:
        """
        resolve a filename and return its contents as bytes
        """
        content = None

        # TODO como verificar?
        if filename.startswith("http://") or filename.startswith("https://"):
            self.logger.warning(f"retrieving remote attachment from {filename}. SSL check is disabled")

            response = requests.get(filename, verify=False)
            self.logger.debug(response)

            if response.status_code != 200:
                self.logger.warning(f"could not retrieve remote file. Status code: {response.status_code}")
                return None

            content = response.content

        elif self.sftp_opts:
            for label, sftp_opt in self.sftp_opts.items():
                self.logger.debug(f"attempting to retrieve {filename} from sftp {label}")
                with pysftp.Connection(sftp_opt.host, username=sftp_opt.username, password=sftp_opt.password, cnopts=sftp_opt.cnopts) as sftp:
                    try:
                        with sftp.open(filename) as remote_file:
                            self.logger.debug(f"found {filename}. Downloading")
                            remote_file.prefetch()

                            content = remote_file.read()
                            break

                    except (FileNotFoundError, ConnectionException, CredentialException, HostKeysException) as e:
                        self.logger.warning(f"{filename} not found in {sftp_opt.host}: {e}")
        else:
            self.logger.debug(f"retrieving {filename} from local file system")
            with open(filename, 'rb') as open_file:
                content = open_file.read()

        return content
    