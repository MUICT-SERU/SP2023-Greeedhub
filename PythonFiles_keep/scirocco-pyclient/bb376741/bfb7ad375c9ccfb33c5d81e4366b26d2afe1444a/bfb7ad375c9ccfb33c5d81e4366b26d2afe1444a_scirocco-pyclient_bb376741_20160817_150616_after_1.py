import json

from urllib3._collections import HTTPHeaderDict
from urllib3.request import urlencode


class RequestsAdapter(object):
    from_header = "DDS-node-id"

    def __init__(self, api_url, node_id, auth_token, request_manager, request_manager_response_handler):
        self._api_url = api_url
        self._node_id = node_id
        self._auth_token = auth_token
        self.request_manager = request_manager
        self.request_manager_response_handler = request_manager_response_handler

    @property
    def api_url(self):
        return self._api_url

    @property
    def node_id(self):
        return self._node_id

    @property
    def auth_token(self):
        return self._auth_token

    def get_headers(self):

        return {
            self.from_header: self._node_id,
            'Authorization': self._auth_token,
            'Content-Type': 'application/json'
        }

    def get_uri(self, resource):

        url = '/'.join([self.api_url, resource.strip("/")])
        return url

    def request(self, method, resource='', data=None, headers=None):

        method = method.upper()
        url = self.get_uri(resource)

        if isinstance(headers, dict):
            headers.update(self.get_headers())
        else:
            headers = self.get_headers()

        if isinstance(data, dict):

            if method in ['GET', 'DELETE']:
                url = ''.join([url, '?', urlencode(data)])
                data = None
            else:
                data = json.dumps(data)
        requests_res = self.request_manager.urlopen(method, url, headers=headers, body=data)

        res = self.request_manager_response_handler.handle(requests_res)

        return res


class RequestManagerResponseHandler:
    def handle(self, response):
        ro = RequestResponse()
        ro.http_headers = DataTypeConverter.all_to_obj(response.headers)
        ro.http_status = DataTypeConverter.all_to_int(response.status)
        ro.system_data = DataTypeConverter.all_to_obj(response.data)
        if ro.system_data is not None:
            ro.message_data = ro.system_data['data']
            if ro.system_data['data']:
                del ro.system_data['data']
        return ro


class RequestResponse:
    def __init__(self):
        self._system_data = None
        self._message_data = None
        self._http_headers = None
        self._http_status = None

    @property
    def system_data(self):
        return self._system_data

    @system_data.setter
    def system_data(self, data):
        self._system_data = data

    @property
    def message_data(self):
        return self._message_data

    @message_data.setter
    def message_data(self, data):
        self._message_data = data

    @property
    def http_headers(self):
        return self._http_headers

    @http_headers.setter
    def http_headers(self, data):
        self._http_headers = data

    @property
    def http_status(self):
        return self._http_status

    @http_status.setter
    def http_status(self, status):
        self._http_status = status


class DataTypeConverter:
    @staticmethod
    def all_to_obj(data):

        if isinstance(data, str):
            data = json.loads(data)
        elif isinstance(data, bytes):
            try:
                data = json.loads(data.decode("utf8"))
            except ValueError:
                data = None
        elif isinstance(data, HTTPHeaderDict):
            pass
        elif isinstance(data, list):
            pass
        elif isinstance(data, dict):
            pass
        else:
            raise TypeError

        return data

    @staticmethod
    def all_to_int(data):

        if isinstance(data, bytes):
            data = int(data.decode("utf8"))
        elif isinstance(data, str):
            data = int(data)
        elif isinstance(data, int):
            pass
        else:
            raise TypeError

        return data
