import json
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


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class RequestManagerMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def urlopen(self, method, url=None, headers=None, body=None):

        if body is None:
            body = {"data":{}}
        else:
            body = json.loads(body)
        body['data']['method'] = method
        body['data']['url'] = url
        body = json.dumps(body).encode("utf8")

        return Bunch(data=body, headers=headers, status=200)
