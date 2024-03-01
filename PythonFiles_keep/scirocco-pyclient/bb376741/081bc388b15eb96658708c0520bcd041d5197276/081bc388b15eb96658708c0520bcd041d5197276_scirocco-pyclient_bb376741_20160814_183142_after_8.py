import json
from urllib3.request import urlencode

from pyddsclient.httpdao.requestresponse import RequestResponse


class RequestAdapterResponseHandler:
    def handle(self, response):
        ro = RequestResponse()

        ro.http_headers = response.headers
        ro.system_data = response.data
        ro.message_data = ro.system_data.data
        del ro.system_data['data']

        return ro


class RequestsAdapter(object):
    api_url = "https://dds.sandboxwebs.com"
    from_header = "DDS-node-id"

    def __init__(self, node_id, auth_token, request_manager, request_manager_response_handler):
        self._node_id = node_id
        self._auth_token = auth_token
        self.pool = request_manager
        self.request_manager_response_handler = request_manager_response_handler

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

    def get_url(self, resource):

        url = '/'.join([self.api_url, resource.strip("/")])
        return url

    def request(self, method, resource='', data=None, headers=None):

        method = method.upper()
        url = self.get_url(resource)

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
        requests_res = self.pool.urlopen(method, url, headers=headers, body=data)

        res = self.request_manager_response_handler.handle(requests_res)

        return res
