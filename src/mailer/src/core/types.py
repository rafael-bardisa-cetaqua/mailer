from typing import Dict, Literal


MailerConfig = Dict[Literal["sender_addr", "sender_pass", "smtp_server_addr", "smtp_server_port"], str]