import json
from unittest.mock import MagicMock

from client.http.requestadapter import RequestResponse


class RequestAdapterMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def request(self, method, url=None, data=None, headers=None):
        response = RequestResponse()

        if data is not None:
            if 'data' in data.keys():
                response.message_data = data['data']
                del data['data']
            else:
                response.message_data = data
        else:
            data = {"data": {}}
        data['url'] = url
        data['method'] = method
        response.system_data = data
        response.http_status = 200
        response.http_headers = headers
        return response


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class RequestManagerMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def urlopen(self, method, url=None, headers=None, body=None):

        if body is None:
            body = {"data": {}}
        else:
            body = json.loads(body)
        body['data']['method'] = method
        body['data']['url'] = url
        body = json.dumps(body).encode("utf8")

        return Bunch(data=body, headers=headers, status=200)
