import unittest

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

    def test_request(self):

        fields = {"name": "eloy", "test": True}
        headers = {"headerExtra": "extraextra!"}

        res = self.request_adapter.request('GET', '/resource', fields, headers)

        self.assertEquals(3, len(res['headers']))
        self.assertEquals('tok', res['headers']['Authorization'])
        self.assertEquals('extraextra!', res['headers']['headerExtra'])
        self.assertEquals('af123', res['headers']['DDS-node-id'])
        self.assertEquals(res['method'], 'GET')
        self.assertEquals(len(res['fields']), 2)
        self.assertEquals('eloy', res['fields']['name'])
        self.assertTrue(res['fields']['test'])
