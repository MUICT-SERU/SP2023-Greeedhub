import json
from unittest.mock import MagicMock

from urllib3._collections import HTTPHeaderDict

from sciroccoclient.metadata import MetaDataDescriptor, MetaData


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class RequestAdapterMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.response_status = 200

    def request(self, method, url=None, data=None, metadata=None, http_headers=None):

        if http_headers is None:
            http_headers = {}
        if metadata is None:
            metadata = {}
        metadata['method'] = method
        metadata['url'] = url
        return Bunch(payload=data, metadata=metadata, http_status=self.response_status,
                     http_headers=http_headers)


class RequestAdapterMultipleMessagesMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.response_status = 200
        self.system_descriptor = MetaDataDescriptor(MetaData())

    def request(self, method, url=None, data=None, metadata=None, http_headers=None):
        messages = []
        metadata = MetaData()
        metadata.id = "af223425"
        metadata.node_source = "af123"
        for m in range(100):
            messages.append({
                self.system_descriptor.get_http_header_by_field_name('id'): "af12344554",
                self.system_descriptor.get_http_header_by_field_name('node_destination'): "af123",
                self.system_descriptor.get_http_header_by_field_name('node_source'): "af123",
                self.system_descriptor.get_http_header_by_field_name('payload_type'): "af123",
                "payload": "my data"
            })
        return Bunch(payload=messages, metadata=metadata, http_status=self.response_status,
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
