import os
import unittest

from sciroccoclient.httpclient import HTTPClient


class SciroccoTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = HTTPClient('http://localhost', 'af123', 'DEFAULT_TOKEN')
        with open(os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'tux.pdf'), 'rb') as f:
            cls.binary_fixture = f.read()

    def setUp(self):
        self.client.delete_all()