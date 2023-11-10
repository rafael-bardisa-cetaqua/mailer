from dataclasses import dataclass

from pysftp import CnOpts


@dataclass(frozen=True)
class SFTPOpts:
    host: str
    username: str
    password: str
    cnopts: CnOpts
