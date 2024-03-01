import unittest
from client.pyddsclient import PyDDSClient


class PyDDSClientTest(unittest.TestCase):
    def setUp(self):
        self.client = PyDDSClient()

    def test_sum(self):
        self.assertEqual(2, self.client.sum(1, 1))
