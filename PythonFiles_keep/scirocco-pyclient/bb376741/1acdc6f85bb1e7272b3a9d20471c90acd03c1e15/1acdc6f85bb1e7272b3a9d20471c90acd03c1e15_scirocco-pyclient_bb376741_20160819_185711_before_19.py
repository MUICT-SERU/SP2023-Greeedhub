import unittest
from client.client import Client


class ClientTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

