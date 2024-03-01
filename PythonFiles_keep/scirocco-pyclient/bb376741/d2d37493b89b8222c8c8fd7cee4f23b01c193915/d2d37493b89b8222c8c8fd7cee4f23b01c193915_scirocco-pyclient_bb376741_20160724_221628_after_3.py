from unittest.mock import MagicMock


class RequestAdapterMock(MagicMock):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def request(self, method, url=None, fields=None, headers=None):
        return {
            "method": method,
            "url": url,
            "fields": fields,
            "headers": headers
        }

class RequestManagerMock(MagicMock):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def request(self, method, url=None, fields=None, headers=None):
        return {
            "method": method,
            "url": url,
            "fields": fields,
            "headers": headers
        }