import unittest

from client.requestsadapter import RequestsAdapter


class RequestsAdapterTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = RequestsAdapter('af123', 'tok')

    def test_fixed_properties(self):
        self.assertEquals('https://dds.sandboxwebs.com', self.request_adapter.api_url)
        self.assertEquals('DDS-node-id', self.request_adapter.from_header)

    def test_mandatory_properties(self):
        self.assertEquals('af123', self.request_adapter.node_id)
        self.assertEquals('tok', self.request_adapter.auth_token)