import urllib3

class RequestsAdapter(object):
    api_url = "https://dds.sandboxwebs.com"
    from_header = "DDS-node-id"

    def __init__(self, node_id, auth_token):
        self._node_id = node_id
        self._auth_token = auth_token
        self.pool = urllib3.PoolManager()

    def get_headers(self):

        return {
            self.from_header: self._node_id,
            'Authorization': self._auth_token
        }

    def request(self, method, resource='', fields=None, headers=None):

        if isinstance(object, headers):
            headers.update(self.get_headers())
        else:
            headers = self.get_headers()
        url = self.api_url + '/' + resource

        res = self.pool.request(method=method, url=url, fields=fields, headers=headers)

        return res

    @property
    def node_id(self):
        return self._node_id

    @property
    def auth_token(self):
        return self._auth_token

