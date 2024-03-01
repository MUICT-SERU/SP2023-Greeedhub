import json
from unittest.mock import MagicMock

from urllib3._collections import HTTPHeaderDict

from sciroccoclient.systemdata import SystemDataDescriptor, SystemData


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class RequestAdapterMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.response_status = 200

    def request(self, method, url=None, data=None, system_data=None, http_headers=None):

        if http_headers is None:
            http_headers = {}
        if system_data is None:
            system_data = {}
        system_data['method'] = method
        system_data['url'] = url
        return Bunch(message_data=data, system_data=system_data, http_status=self.response_status,
                     http_headers=http_headers)


class RequestAdapterMultipleMessagesMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.response_status = 200
        self.system_descriptor = SystemDataDescriptor(SystemData())

    def request(self, method, url=None, data=None, system_data=None, http_headers=None):
        messages = []
        system_data = SystemData()
        system_data.id = "af223425"
        system_data.fromm = "af123"
        for m in range(100):
            messages.append({
                self.system_descriptor.get_http_header_by_field_name('id'): "af12344554",
                self.system_descriptor.get_http_header_by_field_name('to'): "af123",
                self.system_descriptor.get_http_header_by_field_name('fromm'): "af123",
                self.system_descriptor.get_http_header_by_field_name('data_type'): "af123",
                "data": "my data"
            })
        return Bunch(message_data=messages, system_data=system_data, http_status=self.response_status,
                     http_headers=http_headers)



class RequestManagerMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def urlopen(self, method, url=None, headers=None, body=None, status=200):

        headers_dict = HTTPHeaderDict()
        headers_dict.add('url', url)
        headers_dict.add('method', method)

        if headers is not None and isinstance(headers, dict):
            for k, v in headers.items():
                headers_dict.add(k, v)

        if body is None:
            body = ''.encode()
        elif isinstance(body, dict):
            body = json.dumps(body).encode()
        else:
            body = body.encode()

        return Bunch(data=body, headers=headers_dict, status=status)
