import os
import unittest

import urllib3

from sciroccoclient.clients import HTTPClient


class SciroccoTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_url = 'http://localhost'
        cls.config_node_source = 'af123'
        cls.config_token = 'DEFAULT_TOKEN'
        cls.raw_request = urllib3.PoolManager()
        cls.client = HTTPClient(cls.config_url, cls.config_node_source, cls.config_token)
        with open(os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'tux.pdf'), 'rb') as f:
            cls.binary_fixture = f.read()

    def setUp(self):
        # Properly reseting global dataspace.
        self.raw_request.urlopen('DELETE', '/'.join([self.config_url, 'globalDataSpace']), headers={
            'Authorization': self.config_token
        })
