class TurboSmtpException(Exception):
    pass


class TurboSmtp(object):
    _URL = "https://api.turbo-smtp.com/api/mail/send"

    def __init__(self, user, password):
        self._user = user
        self._password = password

    def send(self, message):
        import urllib2

        req = urllib2.Request(self._URL, self._create_turo_data(message))
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as error:
            raise TurboSmtpException(error)

        self._analyse_response(response)

    def _create_turo_data(self, message):
        import urllib

        turbo_data = {}
        turbo_data["authuser"] = self._user
        turbo_data["authpass"] = self._password
        turbo_data["from"] = message["From"]
        turbo_data["to"] = message["To"]
        turbo_data["cc"] = message["CC"]
        turbo_data["bcc"] = message["BCC"]
        turbo_data["subject"] = message["Subject"]
        turbo_data["mime_raw"] = message.as_string()

        return urllib.urlencode(turbo_data)

    def _analyse_response(self, response):
        import json

        resp_contents = response.read()
        msg = json.loads(resp_contents)

        if msg['message'] != "OK":
            raise TurboSmtpException(resp_contents)
