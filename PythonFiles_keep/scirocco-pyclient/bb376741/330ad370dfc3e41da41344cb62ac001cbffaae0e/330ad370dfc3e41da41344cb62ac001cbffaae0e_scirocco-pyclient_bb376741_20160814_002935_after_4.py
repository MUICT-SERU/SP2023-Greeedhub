from unittest.mock import MagicMock


class RequestAdapterMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def request(self, method, url=None, data=None, headers=None):
        return {
            "method": method,
            "url": url,
            "headers": headers,
            "data": data
        }


class RequestManagerMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def urlopen(self, method, url=None, headers=None, body=None):
        return {
            "method": method,
            "url": url,
            "headers": headers,
            "body": body
        }
