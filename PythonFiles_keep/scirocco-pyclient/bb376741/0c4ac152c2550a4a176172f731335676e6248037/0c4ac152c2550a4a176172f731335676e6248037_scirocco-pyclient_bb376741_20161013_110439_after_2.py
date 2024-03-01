import unittest

from sciroccoclient.client import Client
from sciroccoclient.http.messagedao import MessageDAO
from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from test.mocks import RequestAdapterMock


class ClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_adapter = RequestAdapterMock()
        cls.client = Client(MessageDAO(cls.request_adapter), MessageQueueDAO(cls.request_adapter))

    def test_method_message_get_exists(self):
        self.assertTrue("message_get" in dir(self.client))

    def test_method_message_get_accepts_only_one_param(self):
        self.assertRaises(TypeError, self.client.message_get, "3443", "extraparam")

    def test_method_message_get_all_exists(self):
        self.assertTrue("message_get" in dir(self.client))

    def test_method_message_get_all_noparams(self):
        self.assertRaises(TypeError, self.client.message_get_all, "sd")

    def test_method_message_delete_one_exists(self):
        self.assertTrue("message_delete_one" in dir(self.client))

    def test_method_message_delete_one_accepts_only_one_param(self):
        self.assertRaises(TypeError, self.client.message_delete_one, "ssd", "sds")

    def test_method_message_delete_all_exists(self):
        self.assertTrue("message_delete_all" in dir(self.client))

    def test_method_message_delete_all_noparams(self):
        self.assertRaises(TypeError, self.client.message_delete_all, "sd")

    def test_method_message_update_one_exists(self):
        self.assertTrue("message_update_one" in dir(self.client))

    def test_method_message_update_one_accepts_only_two_params(self):
        self.assertRaises(TypeError, self.client.message_update_one, "sd", "sd", "sd")

    def test_method_mesage_queue_push_exists(self):
        self.assertTrue("message_queue_push" in dir(self.client))

    def test_message_queue_push_accepts_only_two_params(self):
        self.assertRaises(TypeError, self.client.message_queue_push, "sds", "sd", "sd")

    def test_method_mesage_queue_ack_exists(self):
        self.assertTrue("message_queue_ack" in dir(self.client))

    def test_mesage_queue_ack_accepts_only_one_params(self):
        self.assertRaises(TypeError, self.client.message_queue_ack, "sds", "sd")