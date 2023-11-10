import unittest
from src.mailer import EmailAPI

class TestMailer(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_default_connection(self):
        mailer = EmailAPI("test@gmail.com", "nopass")
        self.assertTrue(mailer._is_valid_smtp_connection_settings())

    def test_outlook_smtp_connection(self):
        mailer = EmailAPI("test@outlook.com", "nopass", "smtp-mail.outlook.com")
        self.assertTrue(mailer._is_valid_smtp_connection_settings())

    def test_invalid_connection_falis(self):
        mailer = EmailAPI("test@gmail.com", "nopass", "localhost")
        self.assertFalse(mailer._is_valid_smtp_connection_settings())
