import json
from urllib3.request import urlencode


class RequestsAdapter(object):
    api_url = "https://dds.sandboxwebs.com"
    from_header = "DDS-node-id"

    def __init__(self, node_id, auth_token, request_manager):
        self._node_id = node_id
        self._auth_token = auth_token
        self.pool = request_manager

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
        res = self.pool.urlopen(method, url, headers=headers, body=data)

        return res

    def get_url(self, resource):

        url = '/'.join([self.api_url, resource.strip("/")])
        return url
