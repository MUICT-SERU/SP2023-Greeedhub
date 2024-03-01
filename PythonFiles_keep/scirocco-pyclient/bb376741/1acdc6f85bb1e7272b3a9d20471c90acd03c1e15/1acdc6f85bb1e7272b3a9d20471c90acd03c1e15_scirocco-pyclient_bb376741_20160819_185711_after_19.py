import unittest
from sciroccoclient.client import Client


class ClientTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

