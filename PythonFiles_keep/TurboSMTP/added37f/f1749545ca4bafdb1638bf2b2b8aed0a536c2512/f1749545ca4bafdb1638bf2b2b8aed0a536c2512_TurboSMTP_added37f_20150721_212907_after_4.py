import unittest


class Test_mail(unittest.TestCase):
    def setUp(self):
        import turbosmtp
        import json

        with open("config.config") as fp:
            config = json.load(fp)

        self._to = config["to"]
        self._from = config["from"]
        self._server = turbosmtp.TurboSmtp(config["user"], config["password"])

    @unittest.skip("This sends email!")
    def test_mail(self):
        from email import message

        message = message.Message()
        message["From"] = self._from
        message["To"] = self._to
        message["Subject"] = "This is a test!"

        self._server.send(message)

    @unittest.skip("This sends email!")
    def test_mail_text(self):
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart

        message = MIMEMultipart()
        message["From"] = self._from
        message["To"] = self._to
        message["Subject"] = "This is a test with text!"

        att = MIMEBase('text', 'plain')
        with open(__file__) as fp:
            att.set_payload(fp.read())

        message.attach(att)

        self._server.send(message)

    @unittest.skip("This sends email!")
    def test_mail_with_attachment(self):
        from email.mime.image import MIMEImage
        from email.mime.multipart import MIMEMultipart

        message = MIMEMultipart()
        message["From"] = self._from
        message["To"] = self._to
        message["Subject"] = "This is a test with attachment!"

        with open("test.png", "rb") as fp:
            att = MIMEImage(fp.read(), 'octet-stream')

        message.attach(att)
        self._server.send(message)

    def test_mail_exception(self):
        from email import message
        import turbosmtp

        message = message.Message()
        message["From"] = self._from
        message["To"] = self._to
        message["Subject"] = "This is a test!"

        self._server._URL = "https://not.existing.url.bla.bla.bla.com"

        with self.assertRaises(turbosmtp.TurboSmtpException):
            self._server.send(message)

    def test_mail_exception_no_to_from(self):
        from email import message
        import turbosmtp

        message = message.Message()
        message["Subject"] = "This is a test!"

        with self.assertRaises(turbosmtp.TurboSmtpException):
            self._server.send(message)

if __name__ == "__main__":
    unittest.main()
