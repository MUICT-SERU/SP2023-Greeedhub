import json
import unittest
from urllib3.request import urlencode

from client.requestsadapter import RequestsAdapter
from test.mocks import RequestManagerMock


class RequestsAdapterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_manager = RequestManagerMock()

    def setUp(self):
        self.request_adapter = RequestsAdapter('af123', 'tok', self.request_manager)

    def test_fixed_properties(self):
        self.assertEquals('https://dds.sandboxwebs.com', self.request_adapter.api_url)
        self.assertEquals('DDS-node-id', self.request_adapter.from_header)

    def test_mandatory_properties(self):
        self.assertEquals('af123', self.request_adapter.node_id)
        self.assertEquals('tok', self.request_adapter.auth_token)

    def test_get_url(self):
        root = 'https://dds.sandboxwebs.com'
        self.assertEquals(root + '/resource', self.request_adapter.get_url('/resource'))
        self.assertEquals(root + '/resource/subresource', self.request_adapter.get_url('/resource/subresource/'))

    def test_get_headers(self):
        headers = self.request_adapter.get_headers()
        self.assertEquals(headers['Authorization'], 'tok')
        self.assertEquals(headers['DDS-node-id'], 'af123')

    def test_request_methods_without_body(self):
        data = {"name": "eloy", "test": True}
        headers = {"headerExtra": "extraextra!"}

        for m in ['get', 'delete']:
            res = self.request_adapter.request(m, '/resource', data, headers)

            self.assertEquals(4, len(res['headers']))
            self.assertEquals('tok', res['headers']['Authorization'])
            self.assertEquals('extraextra!', res['headers']['headerExtra'])
            self.assertEquals('af123', res['headers']['DDS-node-id'])
            self.assertEquals(res['method'], m.upper())
            self.assertEquals(res['body'], None)
            self.assertEquals(res['url'], ''.join([self.request_adapter.api_url, '/resource', '?', urlencode(data)]))

    def test_request_methods_with_body(self):
        data = {"name": "eloy", "test": "test"}
        headers = {"headerExtra": "extraextra!"}

        for m in ['post', 'put', 'patch']:
            res = self.request_adapter.request(m, '/resource', data, headers)

            self.assertEquals(4, len(res['headers']))
            self.assertEquals('tok', res['headers']['Authorization'])
            self.assertEquals('extraextra!', res['headers']['headerExtra'])
            self.assertEquals('af123', res['headers']['DDS-node-id'])
            self.assertEquals(res['method'], m.upper())
            self.assertIsInstance(res['body'], str)
            self.assertDictEqual(json.loads(res['body']), data)
            self.assertEquals(res['url'], ''.join([self.request_adapter.api_url, '/resource']))
